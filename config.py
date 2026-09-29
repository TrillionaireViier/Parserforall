"""
=============================================================
  Crypto Ban Monitor — Configuration
  Monitors Twitter/X, Threads, Facebook, Instagram
  for crypto ban/block news in EN, RU, UK
=============================================================
"""

import os
from pathlib import Path

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
TWITTER_BEARER_TOKEN = os.environ.get("TWITTER_BEARER_TOKEN", "YOUR_TWITTER_BEARER_TOKEN")
TWITTER_MAX_RESULTS = 50   # 10–100 for Basic tier

# ─── FACEBOOK / INSTAGRAM  ──────────────────────────────────────────────────
META_ACCESS_TOKEN = os.environ.get("META_ACCESS_TOKEN", "YOUR_META_ACCESS_TOKEN")
FACEBOOK_PAGES = [
    "CoinDesk", "CoinTelegraph", "decrypt.co", "TheBlock",
]
INSTAGRAM_ACCOUNTS = []

# ─── THREADS ────────────────────────────────────────────────────────────────
THREADS_SEARCH_ENABLED = True   # set False to skip if blocked

# ─── GOOGLE SHEETS ──────────────────────────────────────────────────────────
# Accepts either file path OR raw JSON secret string
GOOGLE_SERVICE_ACCOUNT_JSON = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "google_service_account.json")
GOOGLE_SHEET_ID = os.environ.get("GOOGLE_SHEET_ID", "YOUR_GOOGLE_SHEET_ID")
GOOGLE_SHEET_TAB = "Crypto Bans"

# Auto-handle raw JSON string passed in environment variables
if GOOGLE_SERVICE_ACCOUNT_JSON.strip().startswith("{"):
    credentials_path = Path("service_account_credentials.json")
    credentials_path.write_text(GOOGLE_SERVICE_ACCOUNT_JSON, encoding="utf-8")
    GOOGLE_SERVICE_ACCOUNT_JSON = str(credentials_path)

# ─── SCHEDULING ──────────────────────────────────────────────────────────────
POLL_INTERVAL_MINUTES = int(os.environ.get("POLL_INTERVAL_MINUTES", "30"))

# ─── MISC ────────────────────────────────────────────────────────────────────
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
SEEN_IDS_FILE = "seen_ids.json"
RESULTS_JSON_FILE = "results.json"
RESULTS_CSV_FILE = "results.csv"
