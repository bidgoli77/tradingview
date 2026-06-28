from fastapi import FastAPI

from config import APP_NAME, APP_VERSION
from webhook import router as webhook_router

from symbols import get_allowed_symbols

from utils import (
    init_db,
    get_recent_signals,
    get_stats,
    now_utc,
)

from engine import (
    build_symbol_status,
    portfolio_summary,
)

# ---------------------------------------------------
# Initialize Database
# ---------------------------------------------------

init_db()

# ---------------------------------------------------
# FastAPI App
# ---------------------------------------------------

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
)

# ---------------------------------------------------
# Routers
# ---------------------------------------------------

app.include_router(webhook_router)

# ---------------------------------------------------
# Home
# ---------------------------------------------------

@app.get("/")
def home():
    return {
        "status": "online",
        "service": APP_NAME,
        "version": APP_VERSION,
        "phase": "Phase 6 - Production",

        "features": [
            "Webhook",
            "SQLite Database",
            "Duplicate Detection",
            "Allowed Symbols",
            "AI Analysis",
            "Risk Manager",
            "Scoring Engine",
            "Portfolio Engine",
            "Symbol Status",
        ],

        "endpoints": [
            "/health",
            "/symbols",
            "/webhook",
            "/test-webhook",
            "/logs",
            "/stats",
            "/symbol-status",
            "/portfolio",
        ],
    }

# ---------------------------------------------------
# Health
# ---------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": APP_NAME,
        "version": APP_VERSION,
        "time": now_utc(),
    }

# ---------------------------------------------------
# Allowed Symbols
# ---------------------------------------------------

@app.get("/symbols")
def symbols():

    allowed = get_allowed_symbols()

    return {
        "count": len(allowed),
        "symbols": allowed,
    }

# ---------------------------------------------------
# Logs
# ---------------------------------------------------

@app.get("/logs")
def logs():

    signals = get_recent_signals(100)

    return {
        "count": len(signals),
        "signals": signals,
    }

# ---------------------------------------------------
# Statistics
# ---------------------------------------------------

@app.get("/stats")
def stats():
    return get_stats()

# ---------------------------------------------------
# Symbol Status
# ---------------------------------------------------

@app.get("/symbol-status")
def symbol_status():
    return build_symbol_status()

# ---------------------------------------------------
# Portfolio
# ---------------------------------------------------

@app.get("/portfolio")
def portfolio():
    return portfolio_summary()