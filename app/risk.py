from app.config import RISK_PER_TRADE_PERCENT, POSITION_SIZE_PERCENT, DEFAULT_ATR_PERCENT

def analyze_risk(signal: dict) -> dict:
    try:
        price = float(signal.get('price', 0) or 0)
    except Exception:
        price = 0
    side = str(signal.get('signal', '')).upper()
    if price <= 0 or side not in ['BUY', 'SELL']:
        return {'decision': 'REJECT', 'risk_level': 'invalid', 'reason': 'Invalid price or signal'}
    atr_pct = DEFAULT_ATR_PERCENT / 100.0
    if side == 'BUY':
        stop_loss = price * (1 - atr_pct)
        take_profit_1 = price * (1 + atr_pct * 1.5)
        take_profit_2 = price * (1 + atr_pct * 3.0)
    else:
        stop_loss = price * (1 + atr_pct)
        take_profit_1 = price * (1 - atr_pct * 1.5)
        take_profit_2 = price * (1 - atr_pct * 3.0)
    return {
        'decision': 'WATCH',
        'risk_level': 'medium',
        'risk_per_trade_percent': RISK_PER_TRADE_PERCENT,
        'position_size_percent': POSITION_SIZE_PERCENT,
        'stop_loss': round(stop_loss, 4),
        'take_profit_1': round(take_profit_1, 4),
        'take_profit_2': round(take_profit_2, 4),
        'reason': 'Core ATR-style fixed percentage risk model applied'
    }
