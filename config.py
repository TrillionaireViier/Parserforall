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
        # DE (Germany, Austria, Switzerland)
        "Webdesigner gesucht dringend", "wer erstellt mir eine Website", "suche jemanden der Websites baut",
        "brauche Hilfe bei Website-Erstellung", "Angebot für Website Erstellung einholen",
        "Homepage programmieren lassen Kosten", "Webentwickler für Projekt gesucht", "suche Freelancer für Homepage",
        "Online Shop erstellen lassen wer kann helfen", "WordPress Entwickler gesucht", "brauche eine Website",

        # FR (France, Belgium, Switzerland)
        "cherche qqn pour faire mon site internet", "qui peut me créer un site web", "recherche créateur de site internet",
        "devis création site internet professionnel", "combien coûte la création d'un site web", "cherche webmaster freelance",
        "besoin d'aide pour créer mon site", "créer une boutique en ligne recherche développeur",
        "recherche agence ou freelance pour refonte site", "recommande un bon développeur web", "besoin d'un site web urgent",

        # NL (Netherlands, Belgium)
        "wie kan een website voor mij maken", "op zoek naar een goede webbouwer", "website laten ontwerpen offerte",
        "hulp nodig bij maken website", "freelance webdeveloper gezocht", "webshop laten bouwen kosten",
        "wie maakt professionele websites", "programmeur gezocht voor webproject", "zoek een webdesigner voor een website",

        # EN (UK, Ireland, Malta, Global)
        "looking for a web developer to build", "need a website built for my business", "anyone recommend a good web designer",
        "need a programmer to make a website", "looking to hire a front end developer", "quote for custom website development",
        "need someone to build an ecommerce store", "urgently looking for a web designer", "who can build me a modern website",
        "looking for someone to revamp my website", "web developer needed", "hiring developer",

        # ES (Spain)
        "quién me puede hacer una página web", "necesito diseñador web urgente", "presupuesto para crear página web",
        "busco desarrollador web freelance", "crear tienda online busco programador", "alguien recomienda un diseñador web",
        "cuánto cuesta crear una página web", "necesito rehacer mi web", "busco programador para crear web",

        # IT (Italy, Switzerland)
        "chi mi può fare un sito web", "preventivo realizzazione sito internet", "cerco web designer professionista",
        "qualcuno che crea siti web a buon prezzo", "devo rifare il mio sito web", "programmatore per creare e-commerce cercasi",
        "quanto costa far sviluppare un sito", "aiuto per creare sito internet", "ho bisogno di fare un sito",

        # PT (Portugal)
        "quem faz páginas web baratas", "orçamento para criação de website", "preciso de programador para criar site",
        "desenvolvedor web para loja online", "recomendações de web designer", "quero contratar criador de sites",

        # SV / NO / DA (Scandinavia)
        "vem kan hjälpa mig bygga en webbplats", "söker frilansande webbutvecklare", "pris för att bygga en hemsida",
        "behöver ny webbplats för mitt företag", "letar efter någon som kan bygga en hemsida",
        "hvem kan lage en hjemmeside for meg", "trenger webdesigner til nettbutikk", "ønsker tilbud på utvikling av nettside",
        "hvem kan bygge en hjemmeside", "webudvikler søges til projekt", "hvad koster det at få lavet en hjemmeside",

        # FI (Finland)
        "kuka tekisi nettisivut yritykselle", "tarvitsen kotisivut mistä tekijä", "etsitään web-kehittäjää", "paljonko maksaa kotisivujen tekeminen",

        # PL (Poland)
        "kto zrobi stronę internetową", "zlecę wykonanie strony www", "szukam webmastera do sklepu internetowego",
        "potrzebuję programisty do stworzenia strony", "wycena stworzenia strony www", "polecacie kogoś do zrobienia strony",

        # CS / SK (Czechia & Slovakia)
        "kdo mi vytvoří webové stránky", "poptávám tvorbu webových stránek", "hledám šikovného webdesignera", "potřebuji naprogramovat web",
        "kto mi vie spraviť webovú stránku", "hľadám tvorcu webových stránok", "potrebujem vytvoriť e-shop",

        # RO / HU (Romania & Hungary)
        "cine mă poate ajuta să fac un site", "caut web designer profesionist", "cât costă crearea unui site web", "ofertă preț creare site prezentare",
        "weboldal készítéséhez keresek szakembert", "ki tud készíteni egy jó honlapot", "webfejlesztőt keresek vállalkozáshoz",

        # EL / BG / HR / SL (SE Europe)
        "ποιος φτιάχνει επαγγελματικές ιστοσελίδες", "κόστος κατασκευής ιστοσελίδας προσφορά",
        "кой може да ми направи уебсайт", "търся разработчик за онлайн магазин",
        "trebam nekoga za izradu web shopa", "iščem izdelovalca spletnih strani",

        # Ukraine & RU
        "створюю зараз сайт", "сайт заказала", "треба зробити сайт", "потрібен сайт", "шукаю розробника", "нужно сделать сайт"
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

# High Client Intent regex patterns
INTENT_PATTERNS = [
    r"webdesigner\s+gesucht", r"wer\s+erstellt\s+mir\s+eine\s+website", r"suche\s+jemanden\s+der\s+websites",
    r"brauche\s+hilfe\s+bei\s+website", r"homepage\s+programmieren\s+lassen", r"wordpress\s+entwickler\s+gesucht",
    r"cherche\s+qqn\s+pour\s+faire\s+mon\s+site", r"qui\s+peut\s+me\s+créer\s+un\s+site", r"recherche\s+créateur\s+de\s+site",
    r"devis\s+création\s+site", r"cherche\s+webmaster", r"besoin\s+d'aide\s+pour\s+créer\s+mon\s+site",
    r"wie\s+kan\s+een\s+website\s+voor\s+mij\s+maken", r"op\s+zoek\s+naar\s+een\s+goede\s+webbouwer", r"freelance\s+webdeveloper\s+gezocht",
    r"looking\s+for\s+a\s+web\s+developer", r"need\s+a\s+website\s+built", r"anyone\s+recommend\s+a\s+good\s+web\s+designer",
    r"need\s+a\s+programmer\s+to\s+make\s+a\s+website", r"quote\s+for\s+custom\s+website", r"who\s+can\s+build\s+me\s+a\s+modern\s+website",
    r"quién\s+me\s+puede\s+hacer\s+una\s+página\s+web", r"necesito\s+diseñador\s+web", r"presupuesto\s+para\s+crear\s+página\s+web",
    r"busco\s+desarrollador\s+web", r"chi\s+mi\s+può\s+fare\s+un\s+sito", r"preventivo\s+realizzazione\s+sito",
    r"cerco\s+web\s+designer", r"programmatore\s+per\s+creare\s+e-commerce", r"quem\s+faz\s+páginas\s+web",
    r"orçamento\s+para\s+criação\s+de\s+website", r"vem\s+kan\s+hjälpa\s+mig\s+bygga", r"söker\s+frilansande\s+webbutvecklare",
    r"hvem\s+kan\s+lage\s+en\s+hjemmeside", r"hvem\s+kan\s+bygge\s+en\s+hjemmeside", r"kuka\s+tekisi\s+nettisivut",
    r"kto\s+zrobi\s+stronę", r"zlecę\s+wykonanie\s+strony", r"szukam\s+webmastera", r"kdo\s+mi\s+vytvoří\s+webové",
    r"kto\s+mi\s+vie\s+spraviť\s+webovú", r"cine\s+mă\s+poate\s+ajuta", r"weboldal\s+készítéséhez",
    r"ποιος\s+φτιάχνει\s+επαγγελματικές", r"кой\s+може\s+да\s+ми\s+направи\s+уебсайт", r"trebam\s+nekoga\s+za\s+izradu",
    r"iščem\s+izdelovalca", r"створюю\s+зараз\s+сайт", r"сайт\s+заказала", r"треба\s+зробити\s+сайт"
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
