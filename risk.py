def analyze_risk(signal: dict) -> dict:
    price = float(signal.get("price", 0) or 0)
    side = signal.get("signal", "").upper()

    if price <= 0 or side not in ["BUY", "SELL"]:
        return {
            "decision": "REJECT",
            "risk_level": "invalid",
            "reason": "Invalid price or signal",
        }

    risk_percent = 1.0
    position_size_percent = 5.0

    if side == "BUY":
        stop_loss = price * 0.98
        take_profit_1 = price * 1.03
        take_profit_2 = price * 1.06
    else:
        stop_loss = price * 1.02
        take_profit_1 = price * 0.97
        take_profit_2 = price * 0.94

    return {
        "decision": "WATCH",
        "risk_level": "medium",
        "risk_percent": risk_percent,
        "position_size_percent": position_size_percent,
        "stop_loss": round(stop_loss, 4),
        "take_profit_1": round(take_profit_1, 4),
        "take_profit_2": round(take_profit_2, 4),
        "reason": "Basic risk model applied",
    }