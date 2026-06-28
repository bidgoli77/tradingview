from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
import json
import sqlite3
from pathlib import Path

app = FastAPI(title="Mehdi Trading Bot API")

DB_PATH = Path("signals.db")


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


init_db()


def make_duplicate_key(data: dict) -> str:
    symbol = str(data.get("symbol", "")).upper()
    signal = str(data.get("signal", "")).upper()
    timeframe = str(data.get("timeframe", ""))
    event_time = str(data.get("time", ""))
    return f"{symbol}|{signal}|{timeframe}|{event_time}"


def save_signal(data: dict, status: str = "received"):
    duplicate_key = make_duplicate_key(data)

    signal = {
        "received_at": datetime.now(timezone.utc).isoformat(),
        "symbol": str(data.get("symbol", "")).upper(),
        "price": str(data.get("price", "")),
        "event_time": data.get("time"),
        "signal": str(data.get("signal", "")).upper(),
        "timeframe": data.get("timeframe"),
        "exchange": data.get("exchange"),
        "volume": str(data.get("volume", "")),
        "status": status,
        "duplicate_key": duplicate_key,
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


@app.get("/")
def home():
    return {
        "status": "online",
        "service": "Mehdi Trading Bot",
        "phase": "2 - database + duplicate protection",
        "endpoints": ["/webhook", "/logs", "/health", "/test-webhook", "/stats"],
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "time": datetime.now(timezone.utc).isoformat(),
        "database": "connected" if DB_PATH.exists() else "not_created_yet",
    }


@app.post("/webhook")
async def webhook(request: Request):
    try:
        raw = (await request.body()).decode("utf-8")
        data = json.loads(raw)

        required = ["symbol", "price", "signal"]
        missing = [k for k in required if k not in data]

        if missing:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "Missing required fields",
                    "missing": missing,
                    "received": data,
                },
            )

        saved = save_signal(data)

        if saved["is_duplicate"]:
            print("⚠️ DUPLICATE SIGNAL IGNORED:")
        else:
            print("✅ NEW SIGNAL SAVED:")

        print(json.dumps(saved, indent=2))

        return {
            "status": "success",
            "message": "Duplicate ignored" if saved["is_duplicate"] else "Signal saved",
            "signal": saved,
        }

    except json.JSONDecodeError:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "Invalid JSON"},
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)},
        )


@app.get("/webhook")
def webhook_get():
    return {
        "status": "webhook endpoint is active",
        "method": "POST required",
    }


@app.get("/test-webhook")
def test_webhook():
    test_data = {
        "symbol": "BTCUSD",
        "price": "65000",
        "time": datetime.now(timezone.utc).isoformat(),
        "signal": "BUY",
        "timeframe": "1D",
        "exchange": "BITSTAMP",
        "volume": "1000",
    }

    saved = save_signal(test_data, status="test_received")

    return {
        "status": "success",
        "message": "Test signal saved",
        "signal": saved,
    }


@app.get("/logs")
def logs():
    with get_conn() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT *
            FROM signals
            ORDER BY id DESC
            LIMIT 50
        """).fetchall()

    return {
        "total_returned": len(rows),
        "signals": [dict(row) for row in rows],
    }


@app.get("/stats")
def stats():
    with get_conn() as conn:
        total = conn.execute("SELECT COUNT(*) FROM signals").fetchone()[0]
        buys = conn.execute("SELECT COUNT(*) FROM signals WHERE signal='BUY'").fetchone()[0]
        sells = conn.execute("SELECT COUNT(*) FROM signals WHERE signal='SELL'").fetchone()[0]
        duplicates = conn.execute("SELECT COUNT(*) FROM signals WHERE status='duplicate_ignored'").fetchone()[0]

    return {
        "total_signals": total,
        "buy_signals": buys,
        "sell_signals": sells,
        "duplicates_ignored": duplicates,
    }