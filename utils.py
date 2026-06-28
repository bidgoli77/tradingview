import sqlite3
from datetime import datetime, timezone
from config import DB_PATH
from symbols import normalize_symbol


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    with get_conn() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            received_at TEXT NOT NULL,
            symbol TEXT NOT NULL,
            price TEXT,
            event_time TEXT,
            signal TEXT NOT NULL,
            timeframe TEXT,
            exchange TEXT,
            volume TEXT,
            status TEXT NOT NULL,
            duplicate_key TEXT UNIQUE
        )
        """)
        conn.commit()


def make_duplicate_key(data: dict) -> str:
    symbol = normalize_symbol(data.get("symbol", ""))
    signal = str(data.get("signal", "")).upper()
    timeframe = str(data.get("timeframe", ""))
    event_time = str(data.get("time", ""))
    return f"{symbol}|{signal}|{timeframe}|{event_time}"


def save_signal(data: dict, status: str = "received") -> dict:
    normalized_symbol = normalize_symbol(data.get("symbol", ""))

    signal = {
        "received_at": now_utc(),
        "symbol": normalized_symbol,
        "price": str(data.get("price", "")),
        "event_time": data.get("time"),
        "signal": str(data.get("signal", "")).upper(),
        "timeframe": data.get("timeframe"),
        "exchange": data.get("exchange"),
        "volume": str(data.get("volume", "")),
        "status": status,
        "duplicate_key": make_duplicate_key(data),
    }

    try:
        with get_conn() as conn:
            cur = conn.execute("""
                INSERT INTO signals (
                    received_at, symbol, price, event_time, signal,
                    timeframe, exchange, volume, status, duplicate_key
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                signal["received_at"],
                signal["symbol"],
                signal["price"],
                signal["event_time"],
                signal["signal"],
                signal["timeframe"],
                signal["exchange"],
                signal["volume"],
                signal["status"],
                signal["duplicate_key"],
            ))
            conn.commit()

            signal["id"] = cur.lastrowid
            signal["is_duplicate"] = False
            return signal

    except sqlite3.IntegrityError:
        signal["is_duplicate"] = True
        signal["status"] = "duplicate_ignored"
        return signal


def get_recent_signals(limit: int = 50):
    with get_conn() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT *
            FROM signals
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()

    return [dict(row) for row in rows]


def get_stats():
    with get_conn() as conn:
        total = conn.execute("SELECT COUNT(*) FROM signals").fetchone()[0]
        buys = conn.execute("SELECT COUNT(*) FROM signals WHERE signal='BUY'").fetchone()[0]
        sells = conn.execute("SELECT COUNT(*) FROM signals WHERE signal='SELL'").fetchone()[0]

    return {
        "total_signals": total,
        "buy_signals": buys,
        "sell_signals": sells,
    }