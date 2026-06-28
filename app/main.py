from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.config import APP_NAME, APP_VERSION, BASE_DIR
from app.database import init_db
from app.webhook import router as webhook_router
from app.dashboard import router as dashboard_router
from app.symbols import get_allowed_symbols
from app.utils import get_recent_signals, get_stats, now_utc
from app.engine import build_symbol_status, portfolio_summary
from app.backtest import backtest_summary

init_db()

app = FastAPI(title=APP_NAME, version=APP_VERSION)
app.mount('/static', StaticFiles(directory=str(BASE_DIR / 'static')), name='static')
app.include_router(webhook_router)
app.include_router(dashboard_router)

@app.get('/')
def home():
    return {
        'status': 'online',
        'service': APP_NAME,
        'version': APP_VERSION,
        'phase': 'v3.0 Core',
        'features': ['Webhook', 'SQLite', 'Duplicate Detection', 'Allowed Symbols', 'Risk Manager', 'Scoring Engine', 'Portfolio Engine', 'Dashboard', 'Paper Broker Placeholder', 'AI Placeholder'],
        'endpoints': ['/health', '/symbols', '/webhook', '/test-webhook', '/logs', '/stats', '/symbol-status', '/portfolio', '/dashboard', '/backtest']
    }

@app.get('/health')
def health():
    return {'status': 'healthy', 'service': APP_NAME, 'version': APP_VERSION, 'time': now_utc()}

@app.get('/symbols')
def symbols():
    values = get_allowed_symbols()
    return {'count': len(values), 'symbols': values}

@app.get('/logs')
def logs(limit: int = 100):
    rows = get_recent_signals(limit)
    return {'count': len(rows), 'signals': rows}

@app.get('/stats')
def stats():
    return get_stats()

@app.get('/symbol-status')
def symbol_status():
    return build_symbol_status()

@app.get('/portfolio')
def portfolio():
    return portfolio_summary()

@app.get('/backtest')
def backtest():
    return backtest_summary()
