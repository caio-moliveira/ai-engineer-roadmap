import sqlite3
from contextlib import contextmanager
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "receipts.db"

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS receipts (
    id            TEXT PRIMARY KEY,
    description   TEXT,
    amount        REAL,
    purchase_time TEXT,
    location      TEXT,
    raw_text      TEXT,
    created_at    TEXT NOT NULL
)
"""


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    with get_db() as conn:
        conn.execute(_CREATE_TABLE)
