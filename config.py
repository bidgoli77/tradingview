import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "Mehdi Trading Bot"
APP_VERSION = "2.0"
DB_PATH = os.getenv("DB_PATH", "signals.db")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
ENABLE_AI_ANALYSIS = os.getenv("ENABLE_AI_ANALYSIS", "false").lower() == "true"