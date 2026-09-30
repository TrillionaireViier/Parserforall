"""
=============================================================
  Parserforall — Universal Scraper Configuration
  Monitors Threads, Twitter/X, Facebook, Instagram
  Niches: Freelance Projects · Marketing · IT & Web Dev · Business Plans
  Languages: EN, DE, FR, ES, IT, RU, UK
=============================================================
"""

import os
from pathlib import Path

# ─── MULTI-LANGUAGE KEYWORDS ──────────────────────────────────────────────────
KEYWORDS = {
    # ── 1. FREELANCE & HIRING ──
    "freelance": [
        "web developer needed", "looking for developer", "hiring developer",
        "freelance project", "hiring designer", "looking for programmer",
        "suche entwickler", "webentwickler gesucht", "freelancer gesucht",
        "cherche développeur", "recherche développeur web", "mission freelance",
        "se busca desarrollador", "busco programador", "proyecto freelance",
        "cercasi sviluppatore web", "lavoro freelance",
        "нужен разработчик", "ищу программиста", "нужен веб-дизайнер", "фриланс проект",
        "потрібен розробник", "шукаю програміста", "потрібен веб-дизайнер"
    ],
    # ── 2. MARKETING ──
    "marketing": [
        "digital marketing", "seo specialist", "smm manager", "lead generation",
        "growth marketing", "marketing strategy", "content marketing", "media buyer",
        "digitales marketing", "seo spezialist", "marketing strategie",
        "marketing numérique", "stratégie marketing", "gestionnaire smm",
        "marketing digital", "estrategia de marketing", "generación de leads",
        "диджитал маркетинг", "seo специалист", "smm менеджер", "поиск лидов",
        "маркетинг стратегія", "лидогенерация"
    ],
    # ── 3. IT & WEB DEV ──
    "it_webdev": [
        "web development", "fullstack developer", "frontend developer",
        "backend developer", "react developer", "python developer", "app development",
        "software engineering", "ai development", "saas startup", "webdesign",
        "webentwicklung", "softwareentwickler", "app entwicklung",
        "développement web", "développeur fullstack", "création сайт",
        "desarrollo web", "desarrollador fullstack", "programación web",
        "разработка сайтов", "веб-разработка", "создание сайтов", "мобильная разработка",
        "розробка сайтів", "веб-розробка", "створення сайтів"
    ],
    # ── 4. BUSINESS PLANS & STARTUPS ──
    "business_plan": [
        "business plan", "startup pitch", "business development", "pitch deck",
        "investor deck", "business idea", "cofounder wanted", "startup idea",
        "business-plan", "businessplan erstellen", "investorensuche",
        "plan d'affaires", "pitch startup", "recherche investisseur",
        "plan de negocios", "idea de negocio", "busco socio",
        "бизнес план", "стартап питч", "бизнес идея", "поиск инвестора", "ищу партнера",
        "бізнес план", "стартап пітч", "бізнес ідея", "пошук інвестора"
    ]
}

# Flatten to full target search list
ALL_TARGET_CATEGORIES = ["freelance", "marketing", "webdev", "businessplan"]
ALL_KEYWORDS = list(set(kw for kws in KEYWORDS.values() for kw in kws))

# ─── DYNAMIC TARGET SCRAPE PARAMETERS ──────────────────────────────────────
SCRAPE_PLATFORM = os.environ.get("SCRAPE_PLATFORM", "threads")  # threads, twitter, facebook, instagram, all
SCRAPE_MODE = os.environ.get("SCRAPE_MODE", "tag")             # tag / hashtag, user / profile, keyword
SCRAPE_TARGET = os.environ.get("SCRAPE_TARGET", "freelance")    # freelance, marketing, webdev, businessplan
SCRAPE_LIMIT = int(os.environ.get("SCRAPE_LIMIT", "999"))        # post limit (default 999)

# ─── TWITTER / X ────────────────────────────────────────────────────────────
TWITTER_BEARER_TOKEN = os.environ.get("TWITTER_BEARER_TOKEN", "YOUR_TWITTER_BEARER_TOKEN")
TWITTER_MAX_RESULTS = 100   # 10–100 per API page

# ─── FACEBOOK / INSTAGRAM  ──────────────────────────────────────────────────
META_ACCESS_TOKEN = os.environ.get("META_ACCESS_TOKEN", "YOUR_META_ACCESS_TOKEN")
FACEBOOK_PAGES = ["CoinDesk", "CoinTelegraph", "decrypt.co", "TheBlock"]
INSTAGRAM_ACCOUNTS = []

# ─── THREADS ────────────────────────────────────────────────────────────────
THREADS_SEARCH_ENABLED = True

# ─── GOOGLE SHEETS ──────────────────────────────────────────────────────────
GOOGLE_SERVICE_ACCOUNT_JSON = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "google_service_account.json")
GOOGLE_SHEET_ID = os.environ.get("GOOGLE_SHEET_ID", "YOUR_GOOGLE_SHEET_ID")
GOOGLE_SHEET_TAB = "Scraped Leads"

if GOOGLE_SERVICE_ACCOUNT_JSON.strip().startswith("{"):
    credentials_path = Path("service_account_credentials.json")
    credentials_path.write_text(GOOGLE_SERVICE_ACCOUNT_JSON, encoding="utf-8")
    GOOGLE_SERVICE_ACCOUNT_JSON = str(credentials_path)

# ─── SCHEDULING ──────────────────────────────────────────────────────────────
POLL_INTERVAL_MINUTES = int(os.environ.get("POLL_INTERVAL_MINUTES", "15"))

# ─── MISC & OUTPUT FILES ─────────────────────────────────────────────────────
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
SEEN_IDS_FILE = "seen_ids.json"
RESULTS_JSON_FILE = "results.json"
RESULTS_CSV_FILE = "results.csv"
RESULTS_TXT_FILE = "results.txt"
