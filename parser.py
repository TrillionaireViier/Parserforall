"""
=============================================================
  Crypto & Social Media Scraper — Main Parserforall
  Platform Support: Threads.net · Twitter/X · Facebook · Instagram
  Modes: Tag/Hashtag · Profile/User · Keyword Search
  Output:  Google Sheets & Local JSON/CSV Artifacts
=============================================================
"""

import argparse
import csv
import json
import logging
import os
import re
import sys
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
log = logging.getLogger("parserforall")


# ─── HELPERS ─────────────────────────────────────────────────────────────────

import codecs

def clean_unescape_text(text: str) -> str:
    """Safely decode unicode escape sequences like \\u00fc into clean UTF-8 characters."""
    if not isinstance(text, str):
        return ""
    if "\\u" in text or "\\n" in text:
        try:
            json_str = '"' + text.replace('"', '\\"').replace('\n', '\\n') + '"'
            return json.loads(json_str)
        except Exception:
            try:
                return codecs.decode(text, 'unicode_escape')
            except Exception:
                pass
    return text.strip()


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


def classify_client_intent(text: str) -> str:
    """Classify if the post shows strong client intent to order a website or service."""
    if not text:
        return "GENERAL_LEAD"
    low = text.lower()
    for pattern in getattr(config, "INTENT_PATTERNS", []):
        if re.search(pattern, low):
            return "HIGH_CLIENT_INTENT"
    return "GENERAL_LEAD"


def save_local_artifacts(rows: list[list]) -> None:
    """Save results to local JSON, CSV, and TXT files for GitHub Action Artifacts."""
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
        cleaned_text = clean_unescape_text(r[5])
        intent = classify_client_intent(cleaned_text)
        existing_data.append({
            "timestamp": r[0],
            "source": r[1],
            "author": r[2],
            "language": r[3],
            "url": r[4],
            "intent": intent,
            "text": cleaned_text
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

    # 3. Save / Append to results.txt
    txt_path = Path(config.RESULTS_TXT_FILE)
    with open(txt_path, mode="a", encoding="utf-8") as f:
        for r in rows:
            f.write("================================================================================\n")
            f.write(f"Timestamp: {r[0]}\n")
            f.write(f"Source:    {r[1]}\n")
            f.write(f"Author:    {r[2]}\n")
            f.write(f"Language:  {r[3]}\n")
            f.write(f"URL:       {r[4]}\n")
            f.write(f"Content:   {r[5]}\n")
            f.write("================================================================================\n\n")

    log.info("Saved %d rows to local artifacts (%s, %s, %s)", 
             len(rows), config.RESULTS_JSON_FILE, config.RESULTS_CSV_FILE, config.RESULTS_TXT_FILE)


SCAM_SPAM_PATTERNS = [
    r"age:\s*\d{2}\s*to\s*\d{2}",       # e.g. "Age: 22 to 50 can apply"
    r"age\s*\d{2}-\d{2}",               # e.g. "age 18-50"
    r"hk\$\s*\d+",                      # e.g. "HK$25,000"
    r"work\s*style:\s*step\s*by\s*step", # bot template phrase
    r"whatsapp\s*me",                   # whatsapp spam redirect
    r"t\.me/",                          # telegram spam redirect
    r"earn\s*\$\d+\s*daily",            # get rich quick spam
    r"crypto\s*doubler",                # investment scam
    r"go\s*away\s*bot",                  # bot reply noise
]

def is_scam_or_spam(text: str) -> bool:
    """Return True if text matches known scammy/spam bot patterns."""
    if not text or len(text.strip()) < 15:
        return True
    low = text.lower()
    for pattern in SCAM_SPAM_PATTERNS:
        if re.search(pattern, low):
            return True
    return False


def matches_keywords(text: str) -> bool:
    """Return True if text contains any monitored keyword and is not scam/spam."""
    if is_scam_or_spam(text):
        return False
    low = text.lower()
    return any(kw.lower() in low for kw in config.ALL_KEYWORDS)


LANG_PATTERNS = {
    "UK": ["створюю", "сайт", "треба", "потрібен", "шукаю", "хочу", "гарно"],
    "DE": ["brauche", "website", "homepage", "erstellen", "gesucht", "entwickler", "unsere"],
    "FR": ["cherche", "développeur", "créer", "site", "besoin", "urgent", "références"],
    "NL": ["zoek", "webdesigner", "website", "maken", "laten"],
    "ES": ["busco", "programador", "páginas", "haga", "desarrollador", "propuesta"],
    "IT": ["cerco", "sviluppatore", "creare", "sito", "bisogno"],
    "PT": ["preciso", "site", "profissional", "procuro", "alguém", "criar"],
    "EL": ["ψάχνω", "προγραμματιστή", "ιστοσελίδα"],
    "SV": ["letar", "hemsida", "behöver", "hjälp", "skapa"],
    "NO": ["trenger", "hjelp", "lage", "nettside"],
    "DA": ["søger", "der", "lave", "hjemmeside"],
    "FI": ["etsin", "nettisivujen", "tekijää"],
    "ET": ["otsin", "kodulehe", "tegijat"],
    "LV": ["meklēju", "mājas", "lapas"],
    "LT": ["ieškau", "sukurtų", "interneto"],
    "PL": ["szukam", "zrobienia", "strony", "potrzebuję"],
    "CS": ["hledám", "tvorbu", "webu"],
    "SK": ["hľadám", "programátora", "vytvorenie"],
    "HU": ["honlapkészítőt", "keresek"],
    "RO": ["caut", "programator", "site"],
    "BG": ["търся", "изработка", "сайт"],
    "HR": ["tražim", "izradu", "stranice"],
    "SL": ["iščem", "izdelovalca", "strani"],
    "RU": ["ищем", "нужен", "разработчик", "стартапа"],
}

def detect_language(text: str) -> str:
    """Detect European language code from text."""
    if not text:
        return "EN"
    low = text.lower()
    for lang, markers in LANG_PATTERNS.items():
        if any(m in low for m in markers):
            return lang
    return "EN"


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


# ─── THREADS.NET SCRAPER ──────────────────────────────────────────────────────

def fetch_threads(seen: set, mode: str = "tag", target: str = "technology", limit: int = 5) -> list[list]:
    """
    Scrape Threads.net by Tag/Hashtag, User/Profile, or Keyword Search up to limit.
    """
    if not config.THREADS_SEARCH_ENABLED:
        return []

    results = []
    clean_target = target.strip().lstrip('#').lstrip('@')
    
    # Construct target URL based on mode
    if mode.lower() in ["tag", "hashtag"]:
        urls = [
            f"https://www.threads.net/tag/{requests.utils.quote(clean_target)}",
            f"https://www.threads.net/search?q=%23{requests.utils.quote(clean_target)}&serp_type=default"
        ]
        search_desc = f"Hashtag #{clean_target}"
    elif mode.lower() in ["user", "profile"]:
        urls = [f"https://www.threads.net/@{requests.utils.quote(clean_target)}"]
        search_desc = f"Profile @{clean_target}"
    else: # keyword
        urls = [f"https://www.threads.net/search?q={requests.utils.quote(clean_target)}&serp_type=default"]
        search_desc = f"Keyword '{clean_target}'"

    log.info("Threads: Starting scrape for %s (Limit: %d)...", search_desc, limit)

    # 1. Try Playwright Headless Browser (with system Chrome fallback for macOS)
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = None
            for launch_fn in [
                lambda: p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox']),
                lambda: p.chromium.launch(channel="chrome", headless=True, args=['--no-sandbox', '--disable-setuid-sandbox']),
                lambda: p.chromium.launch(channel="msedge", headless=True, args=['--no-sandbox', '--disable-setuid-sandbox']),
                lambda: p.firefox.launch(headless=True),
                lambda: p.webkit.launch(headless=True),
            ]:
                try:
                    browser = launch_fn()
                    break
                except Exception:
                    continue

            if not browser:
                raise RuntimeError("No working Playwright browser engine found")

            context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
            page = context.new_page()

            for target_url in urls:
                if len(results) >= limit:
                    break
                try:
                    page.goto(target_url, wait_until="domcontentloaded", timeout=15000)
                    time.sleep(2)
                    
                    # Scroll down to load content
                    for _ in range(5):
                        page.evaluate("window.scrollBy(0, 1000)")
                        time.sleep(1)

                    content = page.content()
                    
                    post_links = re.findall(r'href="(/@[^/]+/post/([^\s"/]+))"', content)
                    texts = re.findall(r'"text":"([^"]{10,600})"', content)

                    for j, (path, post_code) in enumerate(post_links):
                        if len(results) >= limit:
                            break
                        if post_code in seen:
                            continue
                        user = path.split('/')[1].lstrip('@')
                        text = texts[j] if j < len(texts) else f"Threads post on #{clean_target}"
                        if is_scam_or_spam(text):
                            continue
                        post_url = f"https://www.threads.net{path}"
                        lang = detect_language(text)
                        seen.add(post_code)
                        results.append([now_utc(), "Threads", f"@{user}", lang, post_url, text.replace("\n", " ")])
                except Exception as e:
                    log.debug("Threads Playwright error for %s: %s", target_url, e)

            browser.close()
            log.info("Threads (Playwright): scraped %d matching posts for %s.", len(results), search_desc)
            return results
    except Exception as e:
        log.warning("Playwright not available (%s), using HTTP request fallback.", e)

    # 2. HTTP Fallback
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "X-IG-App-ID": "238260118697367",
        "Accept-Language": "en-US,en;q=0.9",
    }

    for target_url in urls:
        if len(results) >= limit:
            break
        try:
            resp = requests.get(target_url, headers=headers, timeout=12)
            matches = re.findall(r'"identifier":"(\d+)"', resp.text)
            texts = re.findall(r'"text":"([^"]{10,600})"', resp.text)
            users = re.findall(r'"username":"([^"]+)"', resp.text)

            for j, mid in enumerate(matches):
                if len(results) >= limit:
                    break
                if mid in seen:
                    continue
                text = texts[j] if j < len(texts) else f"Threads post on #{clean_target}"
                if is_scam_or_spam(text):
                    continue
                user = users[j] if j < len(users) else (clean_target if mode in ["user", "profile"] else "threads_user")
                post_url = f"https://www.threads.net/@{user}/post/{mid}"
                lang = detect_language(text)
                seen.add(mid)
                results.append([now_utc(), "Threads", f"@{user}", lang, post_url, text.replace("\n", " ")])
        except Exception as e:
            log.debug("Threads HTTP error for %s: %s", target_url, e)

    log.info("Threads (HTTP): scraped %d matching posts.", len(results))
    return results


# ─── TWITTER / X ─────────────────────────────────────────────────────────────

def fetch_twitter(seen: set, target: str = "technology", limit: int = 5) -> list[list]:
    """Search recent tweets via Twitter API v2."""
    if not config.TWITTER_BEARER_TOKEN or config.TWITTER_BEARER_TOKEN.startswith("YOUR"):
        log.warning("Twitter: No bearer token configured, skipping.")
        return []

    results = []
    headers = {"Authorization": f"Bearer {config.TWITTER_BEARER_TOKEN}"}
    base_url = "https://api.twitter.com/2/tweets/search/recent"

    query = f'"{target}" -is:retweet'
    params = {
        "query": query[:512],
        "max_results": min(100, max(10, limit)),
        "tweet.fields": "created_at,author_id,text",
        "expansions": "author_id",
        "user.fields": "username",
    }
    try:
        resp = requests.get(base_url, headers=headers, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        tweets = data.get("data", [])
        users = {u["id"]: u["username"] for u in data.get("includes", {}).get("users", [])}

        for tw in tweets:
            if len(results) >= limit:
                break
            tid = tw["id"]
            if tid in seen:
                continue
            text = tw.get("text", "")
            author = users.get(tw.get("author_id", ""), "unknown")
            url = f"https://x.com/{author}/status/{tid}"
            lang = detect_language(text)
            seen.add(tid)
            results.append([now_utc(), "Twitter/X", f"@{author}", lang, url, text.replace("\n", " ")])
    except Exception as e:
        log.error("Twitter API error: %s", e)

    log.info("Twitter: found %d new matching tweets.", len(results))
    return results


# ─── FACEBOOK ────────────────────────────────────────────────────────────────

def fetch_facebook(seen: set, target: str = "CoinDesk", limit: int = 5) -> list[list]:
    """Fetch recent posts from Facebook Pages via Graph API."""
    if not config.META_ACCESS_TOKEN or config.META_ACCESS_TOKEN.startswith("YOUR"):
        log.warning("Facebook: No access token configured, skipping.")
        return []

    results = []
    base = "https://graph.facebook.com/v19.0"
    token = config.META_ACCESS_TOKEN
    pages = [target] if target else config.FACEBOOK_PAGES

    for page in pages:
        if len(results) >= limit:
            break
        try:
            resp = requests.get(
                f"{base}/{page}/posts",
                params={
                    "access_token": token,
                    "fields": "id,message,created_time,permalink_url",
                    "limit": limit,
                },
                timeout=15,
            )
            resp.raise_for_status()
            posts = resp.json().get("data", [])
        except Exception as e:
            log.error("Facebook API error for page '%s': %s", page, e)
            continue

        for post in posts:
            if len(results) >= limit:
                break
            pid = post.get("id", "")
            if pid in seen:
                continue
            text = post.get("message", "")
            if not text:
                continue
            url = post.get("permalink_url", f"https://www.facebook.com/{pid}")
            lang = detect_language(text)
            seen.add(pid)
            results.append([now_utc(), "Facebook", page, lang, url, text[:500].replace("\n", " ")])

    log.info("Facebook: found %d new matching posts.", len(results))
    return results


# ─── INSTAGRAM ───────────────────────────────────────────────────────────────

def fetch_instagram(seen: set, target: str = "", limit: int = 5) -> list[list]:
    """Fetch recent Instagram Business media via Graph API."""
    if not config.META_ACCESS_TOKEN or config.META_ACCESS_TOKEN.startswith("YOUR"):
        log.warning("Instagram: No access token configured, skipping.")
        return []

    accounts = [target] if target else config.INSTAGRAM_ACCOUNTS
    if not accounts or not accounts[0]:
        log.info("Instagram: No account IDs configured, skipping.")
        return []

    results = []
    base = "https://graph.facebook.com/v19.0"
    token = config.META_ACCESS_TOKEN

    for ig_id in accounts:
        if len(results) >= limit:
            break
        try:
            resp = requests.get(
                f"{base}/{ig_id}/media",
                params={
                    "access_token": token,
                    "fields": "id,caption,permalink,timestamp,username",
                    "limit": limit,
                },
                timeout=15,
            )
            resp.raise_for_status()
            media = resp.json().get("data", [])
        except Exception as e:
            log.error("Instagram API error for account '%s': %s", ig_id, e)
            continue

        for item in media:
            if len(results) >= limit:
                break
            mid = item.get("id", "")
            if mid in seen:
                continue
            text = item.get("caption", "")
            url = item.get("permalink", "")
            user = item.get("username", ig_id)
            lang = detect_language(text)
            seen.add(mid)
            results.append([now_utc(), "Instagram", f"@{user}", lang, url, text[:500].replace("\n", " ")])

    log.info("Instagram: found %d new matching posts.", len(results))
    return results


# ─── MAIN COLLECTION CYCLE ───────────────────────────────────────────────────

def send_webhook(all_rows: list[list], webhook_url: str, platform: str, mode: str, target: str):
    if not webhook_url or not all_rows:
        return
    try:
        formatted_posts = [
            {
                "timestamp": row[0],
                "source": row[1],
                "author": row[2],
                "language": row[3],
                "url": row[4],
                "text": row[5]
            } for row in all_rows
        ]
        payload = {
            "platform": platform,
            "mode": mode,
            "target": target,
            "results": formatted_posts
        }
        res = requests.post(webhook_url, json=payload, timeout=10)
        log.info("Webhook POST to %s status: %d", webhook_url, res.status_code)
    except Exception as e:
        log.warning("Webhook post failed (%s): %s", webhook_url, e)


def run_once(platform: str = None, mode: str = None, target: str = None, limit: int = None, webhook: str = None):
    """Run one collection cycle with dynamic parameters."""
    target_platform = (platform or config.SCRAPE_PLATFORM or "threads").lower()
    target_mode = (mode or config.SCRAPE_MODE or "tag").lower()
    target_name = target or config.SCRAPE_TARGET or "technology"
    target_limit = limit or config.SCRAPE_LIMIT or 5

    log.info("═══ Starting Scraper Cycle [Platform: %s | Mode: %s | Target: %s | Limit: %d] ═══", 
             target_platform, target_mode, target_name, target_limit)

    seen = load_seen_ids()
    ws = get_sheet()
    all_rows: list[list] = []

    if target_platform in ["threads", "threads.net", "all"]:
        all_rows += fetch_threads(seen, mode=target_mode, target=target_name, limit=target_limit)

    if target_platform in ["twitter", "x", "all"]:
        all_rows += fetch_twitter(seen, target=target_name, limit=target_limit)

    if target_platform in ["facebook", "fb", "all"]:
        all_rows += fetch_facebook(seen, target=target_name, limit=target_limit)

    if target_platform in ["instagram", "ig", "all"]:
        all_rows += fetch_instagram(seen, target=target_name, limit=target_limit)

    if all_rows:
        save_local_artifacts(all_rows)
        if ws:
            append_rows_to_sheet(ws, all_rows)
        if webhook or os.environ.get("WEBHOOK_URL"):
            url = webhook or os.environ.get("WEBHOOK_URL")
            send_webhook(all_rows, url, target_platform, target_mode, target_name)
    else:
        log.info("No new matching posts found this cycle.")

    save_seen_ids(seen)
    log.info("═══ Cycle complete. Total parsed rows: %d ═══", len(all_rows))
    return all_rows


def main():
    parser = argparse.ArgumentParser(description="Parserforall — Social & Crypto Media Scraper")
    parser.add_argument("--platform", default=config.SCRAPE_PLATFORM, help="threads, twitter, facebook, instagram, all")
    parser.add_argument("--mode", default=config.SCRAPE_MODE, help="tag, user, keyword")
    parser.add_argument("--target", default=config.SCRAPE_TARGET, help="Target hashtag, username, or search keyword (e.g. technology)")
    parser.add_argument("--limit", type=int, default=config.SCRAPE_LIMIT, help="Max posts to parse (e.g. 5)")
    parser.add_argument("--webhook", default=os.environ.get("WEBHOOK_URL"), help="Webhook URL to POST JSON results to (e.g. https://parserforall.vercel.app/api)")
    parser.add_argument("--loop", action="store_true", help="Run continuously on interval")

    args = parser.parse_args()

    if args.loop:
        log.info("Continuous mode started. Interval: %d min", config.POLL_INTERVAL_MINUTES)
        while True:
            try:
                run_once(platform=args.platform, mode=args.mode, target=args.target, limit=args.limit, webhook=args.webhook)
            except Exception as e:
                log.error("Unhandled error in cycle: %s", e, exc_info=True)
            log.info("Sleeping %d minutes …", config.POLL_INTERVAL_MINUTES)
            time.sleep(config.POLL_INTERVAL_MINUTES * 60)
    else:
        run_once(platform=args.platform, mode=args.mode, target=args.target, limit=args.limit, webhook=args.webhook)


if __name__ == "__main__":
    main()
