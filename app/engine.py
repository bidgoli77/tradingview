import json
from app.utils import get_recent_signals
from app.symbols import get_allowed_symbols

def _parse_json(value):
    try:
        return json.loads(value or '{}')
    except Exception:
        return {}

def build_symbol_status() -> dict:
    recent = get_recent_signals(limit=500)
    output = {}
    for symbol in get_allowed_symbols():
        rows = [r for r in recent if r.get('symbol') == symbol]
        latest = rows[0] if rows else None
        output[symbol] = {
            'symbol': symbol,
            'has_signal': latest is not None,
            'signals_count': len(rows),
            'last_direction': latest.get('signal') if latest else None,
            'last_price': latest.get('price') if latest else None,
            'last_time': latest.get('received_at') if latest else None,
            'decision': latest.get('decision') if latest else None,
            'score': _parse_json(latest.get('score_json')).get('score') if latest else None,
            'state': 'active' if latest else 'waiting',
            'latest_signal': latest,
        }
    return output

def portfolio_summary() -> dict:
    status = build_symbol_status()
    active = [s for s in status.values() if s['has_signal']]
    waiting = [s for s in status.values() if not s['has_signal']]
    return {
        'total_symbols': len(status),
        'active_symbols': len(active),
        'waiting_symbols': len(waiting),
        'buy_symbols': len([s for s in active if s['last_direction'] == 'BUY']),
        'sell_symbols': len([s for s in active if s['last_direction'] == 'SELL']),
        'strong_watch': len([s for s in active if s['decision'] == 'STRONG_WATCH']),
        'symbols': status,
    }
