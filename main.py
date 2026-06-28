from fastapi import FastAPI

from config import APP_NAME, APP_VERSION
from webhook import router as webhook_router
from symbols import get_allowed_symbols
from utils import init_db, get_recent_signals, get_stats, now_utc

init_db()

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
)

app.include_router(webhook_router)


@app.get("/")
def home():
    return {
        "status": "online",
        "service": APP_NAME,
        "version": APP_VERSION,
        "phase": "3 - symbols + database + duplicate protection",
        "endpoints": [
            "/health",
            "/symbols",
            "/webhook",
            "/test-webhook",
            "/logs",
            "/stats",
        ],
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "time": now_utc(),
    }


@app.get("/symbols")
def symbols():
    allowed = get_allowed_symbols()
    return {
        "allowed_symbols_count": len(allowed),
        "allowed_symbols": allowed,
    }


@app.get("/logs")
def logs():
    signals = get_recent_signals()
    return {
        "total_returned": len(signals),
        "signals": signals,
    }


@app.get("/stats")
def stats():
    return get_stats()