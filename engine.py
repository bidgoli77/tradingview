from utils import get_recent_signals
from symbols import get_allowed_symbols


def build_symbol_status() -> dict:
    symbols = get_allowed_symbols()
    recent_signals = get_recent_signals(limit=500)

    status = {}

    for symbol in symbols:
        symbol_signals = [
            s for s in recent_signals
            if s.get("symbol") == symbol
        ]

        latest = symbol_signals[0] if symbol_signals else None

        status[symbol] = {
            "symbol": symbol,
            "has_signal": latest is not None,
            "latest_signal": latest,
            "signals_count": len(symbol_signals),
            "last_direction": latest.get("signal") if latest else None,
            "last_price": latest.get("price") if latest else None,
            "last_time": latest.get("received_at") if latest else None,
            "state": "active" if latest else "waiting",
        }

    return status


def portfolio_summary() -> dict:
    status = build_symbol_status()

    active = [s for s in status.values() if s["has_signal"]]
    waiting = [s for s in status.values() if not s["has_signal"]]

    buys = [s for s in active if s["last_direction"] == "BUY"]
    sells = [s for s in active if s["last_direction"] == "SELL"]

    return {
        "total_symbols": len(status),
        "active_symbols": len(active),
        "waiting_symbols": len(waiting),
        "buy_symbols": len(buys),
        "sell_symbols": len(sells),
        "symbols": status,
    }