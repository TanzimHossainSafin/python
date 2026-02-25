import os
import sys

from dotenv import load_dotenv

load_dotenv()

# ── PostgreSQL ─────────────────────────────────────────────────────────
DB_HOST     = os.getenv("DB_HOST",     "localhost")
DB_PORT     = int(os.getenv("DB_PORT", "5432"))
DB_NAME     = os.getenv("DB_NAME",     "samsung_advisor")
DB_USER     = os.getenv("DB_USER",     "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# ── Anthropic ──────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# ── Scraper ────────────────────────────────────────────────────────────
SCRAPE_TARGET = int(os.getenv("SCRAPE_TARGET", "25"))

# ── Startup validation ─────────────────────────────────────────────────
_missing = [k for k, v in {"ANTHROPIC_API_KEY": ANTHROPIC_API_KEY}.items() if not v]
if _missing:
    sys.exit(f"ERROR: Missing required environment variables: {', '.join(_missing)}. "
             "Copy .env.example to .env and fill in your values.")
