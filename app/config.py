import os
from pathlib import Path
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

APP_NAME = os.getenv('APP_NAME', 'Mehdi Trading Bot')
APP_VERSION = os.getenv('APP_VERSION', '3.0-core')
ENV = os.getenv('ENV', 'production')
DB_PATH = os.getenv('DB_PATH', 'signals.db')
BASE_DIR = Path(__file__).resolve().parent.parent

ENABLE_AI_ANALYSIS = os.getenv('ENABLE_AI_ANALYSIS', 'false').lower() == 'true'
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')

ENABLE_TELEGRAM = os.getenv('ENABLE_TELEGRAM', 'false').lower() == 'true'
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

RISK_PER_TRADE_PERCENT = float(os.getenv('RISK_PER_TRADE_PERCENT', '1.0'))
POSITION_SIZE_PERCENT = float(os.getenv('POSITION_SIZE_PERCENT', '5.0'))
DEFAULT_ATR_PERCENT = float(os.getenv('DEFAULT_ATR_PERCENT', '2.0'))
