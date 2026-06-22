"""
=============================================================
  Crypto Ban Monitor — Main Parser
  Sources: Twitter/X · Threads · Facebook · Instagram
  Output:  Google Sheets
=============================================================
"""

import json
import logging
import time
import re
from datetime import datetime, timezone
from pathlib import Path

import requests
import gspread
from google.oauth2.service_account import Credentials

import config

# ─── LOGGING ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("parser.log", encoding="utf-8"),
    ],
)
log = logging.getLogger("crypto-ban-monitor")


# ─── HELPERS ─────────────────────────────────────────────────────────────────

def load_seen_ids() -> set:
    """Load already-processed post IDs from disk."""
    p = Path(config.SEEN_IDS_FILE)
    if p.exists():
        return set(json.loads(p.read_text(encoding="utf-8")))
    return set()


def save_seen_ids(seen: set) -> None:
    """Persist post IDs to disk."""
    Path(config.SEEN_IDS_FILE).write_text(
        json.dumps(list(seen)), encoding="utf-8"
    )


def matches_keywords(text: str) -> bool:
    """Return True if text contains any monitored keyword (case-insensitive)."""
    low = text.lower()
    return any(kw.lower() in low for kw in config.ALL_KEYWORDS)


def detect_language(text: str) -> str:
    """Naïve language detection based on keyword match."""
    low = text.lower()
    for lang, kws in config.KEYWORDS.items():
        if any(kw.lower() in low for kw in kws):
            return lang.upper()
    return "UNK"


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


# ─── GOOGLE SHEETS ───────────────────────────────────────────────────────────

def get_sheet():
    """Authenticate and return the target worksheet."""
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_file(
        config.GOOGLE_SERVICE_ACCOUNT_JSON, scopes=scopes
    )
    client = gspread.authorize(creds)
    sh = client.open_by_key(config.GOOGLE_SHEET_ID)
    try:
        ws = sh.worksheet(config.GOOGLE_SHEET_TAB)
    except gspread.exceptions.WorksheetNotFound:
        ws = sh.add_worksheet(title=config.GOOGLE_SHEET_TAB, rows=10000, cols=10)
        # Write header row
        ws.append_row(
            ["Timestamp", "Source", "Author", "Language", "URL", "Text"],
            value_input_option="RAW",
        )
    return ws


def append_rows_to_sheet(ws, rows: list[list]) -> None:
    """Append multiple rows to worksheet at once."""
    if not rows:
        return
    ws.append_rows(rows, value_input_option="RAW")
    log.info("Appended %d rows to Google Sheets.", len(rows))


# ─── TWITTER / X ─────────────────────────────────────────────────────────────

def fetch_twitter(seen: set) -> list[list]:
    """
    Search recent tweets via Twitter API v2 (Bearer Token auth).
    Returns list of rows ready for Sheets.
    """
    if not config.TWITTER_BEARER_TOKEN or config.TWITTER_BEARER_TOKEN.startswith("YOUR"):
        log.warning("Twitter: No bearer token configured, skipping.")
        return []

    results = []
    headers = {"Authorization": f"Bearer {config.TWITTER_BEARER_TOKEN}"}
    base_url = "https://api.twitter.com/2/tweets/search/recent"

    # Build OR query from keyword list (max 512 chars for Basic tier)
    # We chunk keywords to stay under the limit
    all_kws = config.ALL_KEYWORDS
    chunk_size = 15
    for i in range(0, len(all_kws), chunk_size):
        chunk = all_kws[i : i + chunk_size]
        query = " OR ".join(f'"{kw}"' for kw in chunk)
        query = f"({query}) -is:retweet lang:en OR lang:ru OR lang:uk"

        params = {
            "query": query[:512],
            "max_results": config.TWITTER_MAX_RESULTS,
            "tweet.fields": "created_at,author_id,text",
            "expansions": "author_id",
            "user.fields": "username",
        }
        try:
            resp = requests.get(base_url, headers=headers, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            log.error("Twitter API error: %s", e)
            continue

        tweets = data.get("data", [])
        users = {u["id"]: u["username"] for u in data.get("includes", {}).get("users", [])}

        for tw in tweets:
            tid = tw["id"]
            if tid in seen:
                continue
            text = tw.get("text", "")
            if not matches_keywords(text):
                continue
            author = users.get(tw.get("author_id", ""), "unknown")
            url = f"https://x.com/{author}/status/{tid}"
            lang = detect_language(text)
            seen.add(tid)
            results.append([now_utc(), "Twitter/X", f"@{author}", lang, url, text.replace("\n", " ")])

    log.info("Twitter: found %d new matching tweets.", len(results))
    return results


# ─── THREADS ─────────────────────────────────────────────────────────────────

def fetch_threads(seen: set) -> list[list]:
    """
    Search Threads via unofficial scraping (no public API yet).
    Uses the 'nodriver' approach via ntscraper if available,
    otherwise falls back to a Threads search URL scrape.
    """
    if not config.THREADS_SEARCH_ENABLED:
        return []

    results = []
    try:
        from ntscraper import Nitter  # type: ignore
        # ntscraper can sometimes scrape Threads via Nitter instances
        # but primary use is Twitter fallback; we use requests here instead
    except ImportError:
        pass

    # Threads v1 API (internal, may break)
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; CryptoBanMonitor/1.0)",
        "X-IG-App-ID": "238260118697367",
    }

    for kw in config.ALL_KEYWORDS[:10]:   # limit to avoid rate limits
        try:
            url = f"https://www.threads.net/search?q={requests.utils.quote(kw)}&serp_type=default"
            resp = requests.get(url, headers=headers, timeout=10)
            # Parse post IDs from page HTML (Threads embeds JSON-LD)
            matches = re.findall(r'"identifier":"(\d+)"', resp.text)
            texts = re.findall(r'"text":"([^"]{20,500})"', resp.text)
            users = re.findall(r'"alternateName":"([^"]+)"', resp.text)

            for j, mid in enumerate(matches):
                if mid in seen:
                    continue
                text = texts[j] if j < len(texts) else kw
                if not matches_keywords(text):
                    continue
                user = users[j] if j < len(users) else "unknown"
                post_url = f"https://www.threads.net/@{user}/post/{mid}"
                lang = detect_language(text)
                seen.add(mid)
                results.append([now_utc(), "Threads", f"@{user}", lang, post_url, text.replace("\n", " ")])
        except Exception as e:
            log.debug("Threads scrape error for '%s': %s", kw, e)

    log.info("Threads: found %d new matching posts.", len(results))
    return results


# ─── FACEBOOK ────────────────────────────────────────────────────────────────

def fetch_facebook(seen: set) -> list[list]:
    """
    Fetch recent posts from configured Facebook Pages via Graph API.
    Requires a Page Access Token with pages_read_engagement permission.
    """
    if not config.META_ACCESS_TOKEN or config.META_ACCESS_TOKEN.startswith("YOUR"):
        log.warning("Facebook: No access token configured, skipping.")
        return []

    results = []
    base = "https://graph.facebook.com/v19.0"
    token = config.META_ACCESS_TOKEN

    for page in config.FACEBOOK_PAGES:
        try:
            # Get page posts
            resp = requests.get(
                f"{base}/{page}/posts",
                params={
                    "access_token": token,
                    "fields": "id,message,created_time,permalink_url",
                    "limit": 25,
                },
                timeout=15,
            )
            resp.raise_for_status()
            posts = resp.json().get("data", [])
        except Exception as e:
            log.error("Facebook API error for page '%s': %s", page, e)
            continue

        for post in posts:
            pid = post.get("id", "")
            if pid in seen:
                continue
            text = post.get("message", "")
            if not text or not matches_keywords(text):
                continue
            url = post.get("permalink_url", f"https://www.facebook.com/{pid}")
            lang = detect_language(text)
            seen.add(pid)
            results.append([now_utc(), "Facebook", page, lang, url, text[:500].replace("\n", " ")])

    log.info("Facebook: found %d new matching posts.", len(results))
    return results


# ─── INSTAGRAM ───────────────────────────────────────────────────────────────

def fetch_instagram(seen: set) -> list[list]:
    """
    Fetch recent Instagram Business media via Graph API.
    Requires the same Meta token with instagram_basic permission.
    """
    if not config.META_ACCESS_TOKEN or config.META_ACCESS_TOKEN.startswith("YOUR"):
        log.warning("Instagram: No access token configured, skipping.")
        return []

    if not config.INSTAGRAM_ACCOUNTS:
        log.info("Instagram: No account IDs configured, skipping.")
        return []

    results = []
    base = "https://graph.facebook.com/v19.0"
    token = config.META_ACCESS_TOKEN

    for ig_id in config.INSTAGRAM_ACCOUNTS:
        try:
            resp = requests.get(
                f"{base}/{ig_id}/media",
                params={
                    "access_token": token,
                    "fields": "id,caption,permalink,timestamp,username",
                    "limit": 20,
                },
                timeout=15,
            )
            resp.raise_for_status()
            media = resp.json().get("data", [])
        except Exception as e:
            log.error("Instagram API error for account '%s': %s", ig_id, e)
            continue

        for item in media:
            mid = item.get("id", "")
            if mid in seen:
                continue
            text = item.get("caption", "")
            if not text or not matches_keywords(text):
                continue
            url = item.get("permalink", "")
            user = item.get("username", ig_id)
            lang = detect_language(text)
            seen.add(mid)
            results.append([now_utc(), "Instagram", f"@{user}", lang, url, text[:500].replace("\n", " ")])

    log.info("Instagram: found %d new matching posts.", len(results))
    return results


# ─── MAIN LOOP ───────────────────────────────────────────────────────────────

def run_once():
    """Run one full collection cycle across all platforms."""
    log.info("═══ Starting collection cycle ═══")
    seen = load_seen_ids()

    ws = get_sheet()

    all_rows: list[list] = []
    all_rows += fetch_twitter(seen)
    all_rows += fetch_threads(seen)
    all_rows += fetch_facebook(seen)
    all_rows += fetch_instagram(seen)

    if all_rows:
        append_rows_to_sheet(ws, all_rows)
    else:
        log.info("No new matching posts found this cycle.")

    save_seen_ids(seen)
    log.info("═══ Cycle complete. Total new rows: %d ═══", len(all_rows))


def main():
    log.info("Crypto Ban Monitor started. Interval: %d min", config.POLL_INTERVAL_MINUTES)
    while True:
        try:
            run_once()
        except Exception as e:
            log.error("Unhandled error in cycle: %s", e, exc_info=True)
        log.info("Sleeping %d minutes …", config.POLL_INTERVAL_MINUTES)
        time.sleep(config.POLL_INTERVAL_MINUTES * 60)


if __name__ == "__main__":
    main()
