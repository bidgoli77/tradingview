def score_signal(signal: dict, risk: dict, ai: dict) -> dict:
    score = 50
    reasons = []

    side = str(signal.get("signal", "")).upper()
    timeframe = str(signal.get("timeframe", "")).upper()
    is_duplicate = signal.get("is_duplicate", False)

    if side in ["BUY", "SELL"]:
        score += 10
        reasons.append("Valid signal direction")

    if timeframe in ["1D", "D", "1W", "W"]:
        score += 15
        reasons.append("Higher timeframe signal")
    elif timeframe in ["4H", "240"]:
        score += 10
        reasons.append("4H signal")
    elif timeframe in ["1H", "60"]:
        score += 5
        reasons.append("1H signal")

    if risk.get("decision") == "WATCH":
        score += 10
        reasons.append("Risk model accepted signal")

    if risk.get("risk_level") == "medium":
        score += 5
        reasons.append("Risk level is acceptable")

    if ai.get("decision") in ["pass", "not_analyzed"]:
        score += 5
        reasons.append("AI filter did not reject signal")

    if is_duplicate:
        score = 0
        reasons.append("Duplicate signal ignored")

    score = max(0, min(score, 100))

    if score >= 85:
        decision = "STRONG_WATCH"
    elif score >= 70:
        decision = "WATCH"
    elif score >= 55:
        decision = "WEAK_WATCH"
    else:
        decision = "IGNORE"

    return {
        "score": score,
        "decision": decision,
        "reasons": reasons,
    }