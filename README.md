# Crypto Ban Monitor — Parserforall

Автоматичний парсер публікацій про **бани/блокування в крипті** у соціальних мережах із виводом у **Google Sheets** та **GitHub Actions**.

## ⚡ Запуск через GitHub Actions (Без серверу)

Ви можете запускати парсер автоматично кожні 6 годин або вручну через вкладку **Actions**:

1. Перейдіть до розділу **[Actions](../../actions)** на GitHub.
2. Оберіть workflow **Run Parserforall (Social & Crypto Monitor)**.
3. Натисніть **Run workflow** -> **Run workflow**.
4. Отримайте згенерований `parser.log` та результат у **Artifacts** або в вашій **Google Sheets**!

### 🔑 Налаштування GitHub Secrets (для автоматичного запуску)

Перейдіть у **Settings** -> **Secrets and variables** -> **Actions** -> **New repository secret**:

| Secret Name | Опис |
|-------------|------|
| `TWITTER_BEARER_TOKEN` | Bearer Token від Twitter API v2 |
| `META_ACCESS_TOKEN` | Token від Meta Graph API |
| `GOOGLE_SHEET_ID` | ID вашої Google Таблиці |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Вміст JSON файлу ключа Service Account |

---

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

### 3. Вказати конфігурацію в `config.py`

### 4. Запустити локально
```bash
python parser.py
```

## Ліцензія

MIT — вільне використання та модифікація.
