#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────
#  Crypto Ban Monitor — Quick Setup Script
# ──────────────────────────────────────────────────────────
set -e

echo "🔧 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "📦 Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit config.py — fill in your API keys:"
echo "     • TWITTER_BEARER_TOKEN"
echo "     • META_ACCESS_TOKEN"
echo "     • GOOGLE_SHEET_ID"
echo "     • GOOGLE_SERVICE_ACCOUNT_JSON (path to your .json key file)"
echo ""
echo "  2. Activate the venv:"
echo "     source venv/bin/activate"
echo ""
echo "  3. Run the parser:"
echo "     python parser.py"
echo ""
echo "  4. Or run once (no loop):"
echo "     python -c 'from parser import run_once; run_once()'"
