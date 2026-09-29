"""
=============================================================
  Crypto Ban Monitor — Main Parser
  Sources: Twitter/X · Threads · Facebook · Instagram
  Output:  Google Sheets & Local JSON/CSV Artifacts
=============================================================
"""

import csv
import json
import logging
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

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
        try:
            return set(json.loads(p.read_text(encoding="utf-8")))
        except Exception as e:
            log.warning("Failed to load seen_ids.json: %s", e)
    return set()


def save_seen_ids(seen: set) -> None:
    """Persist post IDs to disk."""
    Path(config.SEEN_IDS_FILE).write_text(
        json.dumps(list(seen)), encoding="utf-8"
    )


def save_local_artifacts(rows: list[list]) -> None:
    """Save results to local JSON & CSV files for GitHub Action Artifacts."""
    if not rows:
        return

    # 1. Save / Append to results.json
    existing_data = []
    json_path = Path(config.RESULTS_JSON_FILE)
    if json_path.exists():
        try:
            existing_data = json.loads(json_path.read_text(encoding="utf-8"))
        except Exception:
            existing_data = []

    for r in rows:
        existing_data.append({
            "timestamp": r[0],
            "source": r[1],
            "author": r[2],
            "language": r[3],
            "url": r[4],
            "text": r[5]
        })

    json_path.write_text(json.dumps(existing_data, indent=2, ensure_ascii=False), encoding="utf-8")

    # 2. Save / Append to results.csv
    csv_path = Path(config.RESULTS_CSV_FILE)
    file_exists = csv_path.exists()
    with open(csv_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Source", "Author", "Language", "URL", "Text"])
        for r in rows:
            writer.writerow(r)

    log.info("Saved %d rows to local artifacts (%s, %s)", len(rows), config.RESULTS_JSON_FILE, config.RESULTS_CSV_FILE)


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
    """Authenticate and return the target worksheet if configured."""
    if not config.GOOGLE_SHEET_ID or config.GOOGLE_SHEET_ID.startswith("YOUR"):
        log.warning("Google Sheets: GOOGLE_SHEET_ID not set, skipping Sheets export.")
        return None

    if not Path(config.GOOGLE_SERVICE_ACCOUNT_JSON).exists():
        log.warning("Google Sheets: Service account file '%s' not found, skipping Sheets export.", config.GOOGLE_SERVICE_ACCOUNT_JSON)
        return None

    try:
        import gspread
        from google.oauth2.service_account import Credentials

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
        except Exception:
            ws = sh.add_worksheet(title=config.GOOGLE_SHEET_TAB, rows=10000, cols=10)
            ws.append_row(
                ["Timestamp", "Source", "Author", "Language", "URL", "Text"],
                value_input_option="RAW",
            )
        return ws
    except Exception as e:
        log.error("Google Sheets authentication error: %s", e)
        return None


def append_rows_to_sheet(ws, rows: list[list]) -> None:
    """Append multiple rows to worksheet at once."""
    if not ws or not rows:
        return
    try:
        ws.append_rows(rows, value_input_option="RAW")
        log.info("Appended %d rows to Google Sheets.", len(rows))
    except Exception as e:
        log.error("Error appending to Google Sheets: %s", e)


# ─── TWITTER / X ─────────────────────────────────────────────────────────────

def fetch_twitter(seen: set) -> list[list]:
    """Search recent tweets via Twitter API v2 (Bearer Token auth)."""
    if not config.TWITTER_BEARER_TOKEN or config.TWITTER_BEARER_TOKEN.startswith("YOUR"):
        log.warning("Twitter: No bearer token configured, skipping.")
        return []

    results = []
    headers = {"Authorization": f"Bearer {config.TWITTER_BEARER_TOKEN}"}
    base_url = "https://api.twitter.com/2/tweets/search/recent"

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
    """Search Threads via web scraping parser."""
    if not config.THREADS_SEARCH_ENABLED:
        return []

    results = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "X-IG-App-ID": "238260118697367",
        "Accept-Language": "en-US,en;q=0.9",
    }

    for kw in config.ALL_KEYWORDS[:12]:
        try:
            url = f"https://www.threads.net/search?q={requests.utils.quote(kw)}&serp_type=default"
            resp = requests.get(url, headers=headers, timeout=10)
            
            matches = re.findall(r'"identifier":"(\d+)"', resp.text)
            texts = re.findall(r'"text":"([^"]{15,500})"', resp.text)
            users = re.findall(r'"username":"([^"]+)"', resp.text)

            for j, mid in enumerate(matches):
                if mid in seen:
                    continue
                text = texts[j] if j < len(texts) else kw
                user = users[j] if j < len(users) else "user"
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
    """Fetch recent posts from Facebook Pages via Graph API."""
    if not config.META_ACCESS_TOKEN or config.META_ACCESS_TOKEN.startswith("YOUR"):
        log.warning("Facebook: No access token configured, skipping.")
        return []

    results = []
    base = "https://graph.facebook.com/v19.0"
    token = config.META_ACCESS_TOKEN

    for page in config.FACEBOOK_PAGES:
        try:
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
    """Fetch recent Instagram Business media via Graph API."""
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
        save_local_artifacts(all_rows)
        if ws:
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
