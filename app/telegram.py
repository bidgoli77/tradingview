from app.config import ENABLE_TELEGRAM, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

def notify_signal(signal: dict, risk: dict, score: dict) -> dict:
    if not ENABLE_TELEGRAM:
        return {'sent': False, 'reason': 'Telegram disabled'}
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return {'sent': False, 'reason': 'Telegram credentials missing'}
    # v3.0 Core placeholder. Network send will be added in v3.3.
    return {'sent': False, 'reason': 'Telegram network sending reserved for v3.3'}
