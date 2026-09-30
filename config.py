"""
=============================================================
  Parserforall — Universal Scraper Configuration
  Monitors Threads, Twitter/X, Facebook, Instagram
  Primary Categories: IT (Web & App Dev) · Marketing · Business Plan
  European Regions: Western Europe, Southern Europe, Northern Europe, Central & Eastern Europe
=============================================================
"""

import os
from pathlib import Path

# ─── 3 PRIMARY CATEGORIES WITH ALL EUROPEAN INTENT PHRASES ─────────────────────
CATEGORIES = {
    # ── 1. IT / WEB & APP DEVELOPMENT ──
    "it": [
        # Western Europe
        "brauche eine website", "wer kann mir eine homepage erstellen", "webentwickler gesucht", "suche entwickler",
        "cherche développeur pour créer un site", "besoin d'un site web urgent", "recherche développeur web",
        "zoek een webdesigner voor een website", "ik wil een website laten maken",
        # Southern Europe
        "busco programador para crear web", "alguien que haga páginas web", "se busca desarrollador",
        "cerco sviluppatore per creare un sito web", "ho bisogno di fare un sito", "cercasi sviluppatore web",
        "preciso de um site profissional", "procuro alguém para criar site",
        "ψάχνω προγραμματιστή για ιστοσελίδα",
        # Northern Europe (Scandinavia & Baltics)
        "letar efter någon som kan bygga en hemsida", "behöver hjälp med att skapa en hemsida",
        "trenger hjelp til å lage en nettside",
        "søger en der kan lave en hjemmeside",
        "etsin nettisivujen tekijää",
        "otsin kodulehe tegijat",
        "meklēju mājas lapas izstrādātāju",
        "ieškau kas sukurtų interneto svetainę",
        # Central & Eastern Europe
        "szukam kogoś do zrobienia strony www", "potrzebuję pilnie strony internetowej",
        "hledám někoho na tvorbu webu",
        "hľadám programátora na vytvorenie webu",
        "honlapkészítőt keresek",
        "caut programator pentru creare site web",
        "търся човек за изработка на сайт",
        "tražim nekoga za izradu web stranice",
        "iščem izdelovalca spletnih strani",
        # Ukraine, US & General
        "створюю зараз сайт", "сайт заказала", "треба зробити сайт", "потрібен сайт", "шукаю розробника",
        "нужно сделать сайт", "заказать сайт", "ищу кто сделает сайт",
        "web developer needed", "looking for developer", "hiring developer", "need a website made",
        "want to build a website", "react developer", "fullstack developer", "python developer", "app development"
    ],

    # ── 2. DIGITAL MARKETING & GROWTH ──
    "marketing": [
        "digital marketing", "seo specialist", "smm manager", "lead generation",
        "growth marketing", "marketing strategy", "content marketing", "media buyer",
        "digitales marketing", "seo spezialist", "marketing strategie",
        "marketing numérique", "stratégie marketing", "gestionnaire smm",
        "marketing digital", "estrategia de marketing", "generación de leads",
        "диджитал маркетинг", "seo специалист", "smm менеджер", "поиск лидов",
        "маркетинг стратегія", "лидогенерация", "маркетинг для бізнесу"
    ],

    # ── 3. BUSINESS PLAN & STARTUPS ──
    "businessplan": [
        "business plan", "startup pitch", "business development", "pitch deck",
        "investor deck", "business idea", "cofounder wanted", "startup idea",
        "business-plan", "businessplan erstellen", "investorensuche",
        "plan d'affaires", "pitch startup", "recherche investisseur",
        "plan de negocios", "idea de negocio", "busco socio",
        "бизнес план", "стартап питч", "бизнес идея", "поиск инвестора", "ищу партнера",
        "бізнес план", "стартап пітч", "бізнес ідея", "пошук інвестора"
    ]
}

# Alias mapping for backward compatibility
KEYWORDS = {
    "it": CATEGORIES["it"],
    "marketing": CATEGORIES["marketing"],
    "business_plan": CATEGORIES["businessplan"]
}

# High Client Intent patterns
INTENT_PATTERNS = [
    r"brauche\s+eine\s+website", r"wer\s+kann\s+mir\s+eine\s+homepage", r"cherche\s+développeur",
    r"besoin\s+d'un\s+site", r"zoek\s+een\s+webdesigner", r"ik\s+wil\s+een\s+website",
    r"busco\s+programador", r"alguien\s+que\s+haga\s+páginas", r"cerco\s+sviluppatore",
    r"ho\s+bisogno\s+di\s+fare\s+un\s+sito", r"preciso\s+de\s+um\s+site", r"procuro\s+alguém\s+para\s+criar\s+site",
    r"ψάχνω\s+προγραμματιστή", r"letar\s+efter\s+någon\s+som\s+kan\s+bygga", r"behöver\s+hjälp\s+med\s+att\s+skapa",
    r"trenger\s+hjelp\s+til\s+å\s+lage", r"søger\s+en\s+der\s+kan\s+lave", r"etsin\s+nettisivujen",
    r"otsin\s+kodulehe", r"meklēju\s+mājas\s+lapas", r"ieškau\s+kas\s+sukurtų",
    r"szukam\s+kogoś\s+do\s+zrobienia\s+strony", r"potrzebuję\s+pilnie\s+strony", r"hledám\s+někoho\s+na\s+tvorbu",
    r"hľadám\s+programátora", r"honlapkészítőt\s+keresek", r"caut\s+programator", r"търся\s+човек\s+за\s+изработка",
    r"tražim\s+nekoga\s+za\s+izradu", r"iščem\s+izdelovalca", r"створюю\s+зараз\s+сайт", r"сайт\s+заказала",
    r"треба\s+зробити\s+сайт", r"потрібен\s+сайт", r"нужно\s+сделать\s+сайт", r"заказать\s+сайт"
]

ALL_TARGET_CATEGORIES = ["it", "marketing", "businessplan"]
ALL_KEYWORDS = list(set(kw for kws in CATEGORIES.values() for kw in kws))

# ─── DYNAMIC TARGET SCRAPE PARAMETERS ──────────────────────────────────────
SCRAPE_PLATFORM = os.environ.get("SCRAPE_PLATFORM", "threads")  # threads, twitter, facebook, instagram, all
SCRAPE_MODE = os.environ.get("SCRAPE_MODE", "tag")             # tag / hashtag, user / profile, keyword
SCRAPE_TARGET = os.environ.get("SCRAPE_TARGET", "it")           # it, marketing, businessplan
SCRAPE_LIMIT = int(os.environ.get("SCRAPE_LIMIT", "999"))        # post limit (default 999)

# ─── TWITTER / X ────────────────────────────────────────────────────────────
TWITTER_BEARER_TOKEN = os.environ.get("TWITTER_BEARER_TOKEN", "YOUR_TWITTER_BEARER_TOKEN")
TWITTER_MAX_RESULTS = 100

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
