"""
database.py – PostgreSQL setup and CRUD helpers for Samsung phones.

Uses a ThreadedConnectionPool so every request shares pre-opened
connections rather than opening and closing one per query.
"""

import logging
from contextlib import contextmanager

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool

from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

logger = logging.getLogger(__name__)

# ── Connection pool ─────────────────────────────────────────────────────

_pool: ThreadedConnectionPool | None = None


def _get_pool() -> ThreadedConnectionPool:
    global _pool
    if _pool is None:
        _pool = ThreadedConnectionPool(
            minconn=2,
            maxconn=10,
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
        )
        logger.info("DB connection pool created (min=2, max=10).")
    return _pool


@contextmanager
def _connection():
    """Yield a pooled connection; rollback on error, always return to pool."""
    pool = _get_pool()
    conn = pool.getconn()
    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    finally:
        pool.putconn(conn)


# ── Schema ─────────────────────────────────────────────────────────────

def initialize_db():
    """Create the samsung_phones table if it doesn't already exist."""
    with _connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS samsung_phones (
                    id           SERIAL PRIMARY KEY,
                    model_name   VARCHAR(255) UNIQUE NOT NULL,
                    release_date VARCHAR(200),
                    display      VARCHAR(500),
                    battery      VARCHAR(200),
                    camera       TEXT,
                    ram          VARCHAR(200),
                    storage      VARCHAR(200),
                    price        VARCHAR(200),
                    full_specs   TEXT,
                    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    logger.info("Database schema ready.")


# ── Write ──────────────────────────────────────────────────────────────

def upsert_phone(data: dict):
    """Insert a phone record, or update it if the model_name already exists."""
    with _connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO samsung_phones
                    (model_name, release_date, display, battery, camera,
                     ram, storage, price, full_specs)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (model_name) DO UPDATE SET
                    release_date = EXCLUDED.release_date,
                    display      = EXCLUDED.display,
                    battery      = EXCLUDED.battery,
                    camera       = EXCLUDED.camera,
                    ram          = EXCLUDED.ram,
                    storage      = EXCLUDED.storage,
                    price        = EXCLUDED.price,
                    full_specs   = EXCLUDED.full_specs
            """, (
                data["model_name"],
                data.get("release_date", "N/A"),
                data.get("display",      "N/A"),
                data.get("battery",      "N/A"),
                data.get("camera",       "N/A"),
                data.get("ram",          "N/A"),
                data.get("storage",      "N/A"),
                data.get("price",        "N/A"),
                data.get("full_specs",   ""),
            ))
            conn.commit()
    logger.info("Upserted: %s", data["model_name"])


# ── Read ───────────────────────────────────────────────────────────────

def get_all_phones() -> list[dict]:
    """Return all phone records ordered by model name."""
    with _connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM samsung_phones ORDER BY model_name")
            return [dict(r) for r in cur.fetchall()]


def search_phones_by_name(name: str) -> list[dict]:
    """Return phones whose model_name contains *name* (case-insensitive)."""
    with _connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM samsung_phones WHERE LOWER(model_name) LIKE LOWER(%s)",
                (f"%{name}%",),
            )
            return [dict(r) for r in cur.fetchall()]
