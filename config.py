"""
=============================================================
  Crypto Ban Monitor — Configuration
  Monitors Twitter/X, Threads, Facebook, Instagram
  for crypto ban/block news in EN, RU, UK
=============================================================
"""

# ─── KEYWORDS ────────────────────────────────────────────────────────────────
KEYWORDS = {
    "en": [
        "crypto banned", "banned crypto", "crypto blocked", "blocked from crypto",
        "crypto account suspended", "exchange ban", "crypto exchange blocked",
        "bitcoin banned", "defi blocked", "nft banned", "crypto regulation ban",
        "wallet blocked", "crypto suspended", "binance banned", "coinbase ban",
        "usdt blocked", "stablecoin ban", "crypto frozen", "account frozen crypto",
        "sanctions crypto", "crypto blacklist",
    ],
    "ru": [
        "крипто заблокировали", "заблокировали криптобиржу", "бан в крипте",
        "крипто бан", "биткоин запретили", "запрет крипты", "заморозили счёт",
        "криптобиржа заблокирована", "крипто заморожено", "санкции крипта",
        "токен заблокирован", "кошелёк заморожен", "binance заблокировали",
        "coinbase бан", "usdt заблокировали", "defi запрет", "криптовалюта запрет",
        "торговля крипто запрещена", "запрет цифровых активов",
    ],
    "uk": [
        "крипту заблокували", "заблокували криптобіржу", "бан у крипті",
        "крипто бан", "біткоїн заборонили", "заборона крипти", "заморозили рахунок",
        "криптобіржа заблокована", "крипто заморожено", "санкції крипта",
        "токен заблокований", "гаманець заморожено", "binance заблокували",
        "coinbase бан", "usdt заблокували", "defi заборона", "криптовалюта заборона",
        "торгівля крипто заборонена", "цифрові активи заборонені",
    ],
}

# Flatten to one list (used by scrapers)
ALL_KEYWORDS = list(set(kw for kws in KEYWORDS.values() for kw in kws))

# ─── TWITTER / X ────────────────────────────────────────────────────────────
TWITTER_BEARER_TOKEN = "YOUR_TWITTER_BEARER_TOKEN"   # https://developer.twitter.com
TWITTER_MAX_RESULTS = 50   # 10–100 for Basic tier

# ─── FACEBOOK / INSTAGRAM  ──────────────────────────────────────────────────
# Meta Graph API (Page token with pages_read_engagement permission)
META_ACCESS_TOKEN = "YOUR_META_ACCESS_TOKEN"
# List of FB Page IDs or usernames to monitor
FACEBOOK_PAGES = [
    "CoinDesk", "CoinTelegraph", "decrypt.co", "TheBlock",
]
# List of IG Business Account IDs to monitor (must be linked to a FB page)
INSTAGRAM_ACCOUNTS = [
    # "17841400000000000",  # example IG Business ID
]

# ─── THREADS ────────────────────────────────────────────────────────────────
# Threads has no public API yet; we scrape via ntscraper / snscrape workaround
THREADS_SEARCH_ENABLED = True   # set False to skip if blocked

# ─── GOOGLE SHEETS ──────────────────────────────────────────────────────────
# 1. Create a Google Cloud project
# 2. Enable Sheets API + Drive API
# 3. Create a Service Account → download JSON key → put path here
GOOGLE_SERVICE_ACCOUNT_JSON = "google_service_account.json"
# ID of the target spreadsheet (from the URL: /spreadsheets/d/<ID>/edit)
GOOGLE_SHEET_ID = "YOUR_GOOGLE_SHEET_ID"
# Name of the worksheet tab
GOOGLE_SHEET_TAB = "Crypto Bans"

# ─── SCHEDULING ──────────────────────────────────────────────────────────────
POLL_INTERVAL_MINUTES = 30   # run parser every N minutes

# ─── MISC ────────────────────────────────────────────────────────────────────
LOG_LEVEL = "INFO"           # DEBUG | INFO | WARNING | ERROR
SEEN_IDS_FILE = "seen_ids.json"   # cache file to avoid duplicates
