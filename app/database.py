import sqlite3
from app.config import DB_PATH

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_conn() as conn:
        conn.execute('''
        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            received_at TEXT NOT NULL,
            symbol TEXT NOT NULL,
            asset_type TEXT,
            market TEXT,
            price TEXT,
            event_time TEXT,
            signal TEXT NOT NULL,
            timeframe TEXT,
            exchange TEXT,
            volume TEXT,
            status TEXT NOT NULL,
            duplicate_key TEXT UNIQUE,
            risk_json TEXT,
            ai_json TEXT,
            score_json TEXT,
            decision TEXT
        )
        ''')
        conn.execute('''
        CREATE TABLE IF NOT EXISTS positions (
            symbol TEXT PRIMARY KEY,
            side TEXT,
            entry_price TEXT,
            quantity TEXT,
            status TEXT,
            updated_at TEXT
        )
        ''')
        conn.commit()
