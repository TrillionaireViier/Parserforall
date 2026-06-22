# Crypto Ban Monitor — Parserforall

Автоматичний парсер публікацій про **бани/блокування в крипті** у соціальних мережах із виводом у **Google Sheets**.

## Платформи

| Джерело | Метод | Статус |
|---------|-------|--------|
| 🐦 Twitter / X | Twitter API v2 (Bearer Token) | ✅ |
| 🧵 Threads | Scraping (internal API) | ✅ |
| 📘 Facebook | Meta Graph API | ✅ |
| 📷 Instagram | Meta Graph API (Business) | ✅ |
| 📊 Google Sheets | gspread + Service Account | ✅ |

## Мови

Парсер відстежує ключові слова трьома мовами:

- 🇬🇧 **English** — `crypto banned`, `exchange blocked`, `bitcoin banned` …
- 🇷🇺 **Русский** — `крипто заблокировали`, `бан в крипте`, `биткоин запретили` …
- 🇺🇦 **Українська** — `крипту заблокували`, `бан у крипті`, `біткоїн заборонили` …

## Налаштування

### 1. Клонувати репозиторій
```bash
git clone https://github.com/TrillionaireViier/Parserforall.git
cd Parserforall
```

### 2. Встановити залежності
```bash
bash setup.sh
source venv/bin/activate
```

### 3. Заповнити `config.py`

| Параметр | Де отримати |
|----------|------------|
| `TWITTER_BEARER_TOKEN` | [developer.twitter.com](https://developer.twitter.com) → App → Keys & Tokens |
| `META_ACCESS_TOKEN` | [developers.facebook.com](https://developers.facebook.com) → Graph API Explorer |
| `GOOGLE_SHEET_ID` | URL таблиці: `/spreadsheets/d/<ID>/edit` |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | [console.cloud.google.com](https://console.cloud.google.com) → Service Accounts → Create Key → JSON |

### 4. Налаштувати Google Sheets

1. Відкрити [Google Cloud Console](https://console.cloud.google.com)
2. Увімкнути **Google Sheets API** та **Google Drive API**
3. Створити **Service Account** → завантажити JSON ключ → покласти у папку проєкту
4. Відкрити Google Sheets → Поділитись із email сервісного акаунту (права редактора)
5. Вказати `GOOGLE_SHEET_ID` і шлях до JSON у `config.py`

### 5. Запустити

```bash
# Одноразово:
python parser.py

# Або як демон (кожні 30 хв):
python parser.py  # зупиняється через Ctrl+C
```

## Структура Google Sheets

| Timestamp | Source | Author | Language | URL | Text |
|-----------|--------|--------|----------|-----|------|
| 2026-06-23 10:00 UTC | Twitter/X | @coindesk | EN | https://x.com/… | Binance banned in… |
| 2026-06-23 10:01 UTC | Facebook | CoinDesk | RU | https://fb.com/… | Бинанс заблокировали… |

## Запуск як системний сервіс (Linux / VPS)

```bash
sudo cp crypto-ban-monitor.service /etc/systemd/system/
# Відредагуйте шляхи у файлі .service
sudo systemctl daemon-reload
sudo systemctl enable crypto-ban-monitor
sudo systemctl start crypto-ban-monitor
sudo systemctl status crypto-ban-monitor
```

## Ліцензія

MIT — вільне використання та модифікація.
