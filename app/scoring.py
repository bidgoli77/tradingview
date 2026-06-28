def score_signal(signal: dict, risk: dict, ai: dict) -> dict:
    score = 50
    reasons = []
    side = str(signal.get('signal', '')).upper()
    timeframe = str(signal.get('timeframe', '')).upper()

    if signal.get('is_duplicate'):
        return {'score': 0, 'decision': 'IGNORE', 'reasons': ['Duplicate signal ignored']}

    if side in ['BUY', 'SELL']:
        score += 10
        reasons.append('Valid signal direction')
    else:
        score -= 35
        reasons.append('Invalid signal direction')

    if timeframe in ['1D', 'D', '1W', 'W']:
        score += 15
        reasons.append('Higher timeframe')
    elif timeframe in ['4H', '240']:
        score += 10
        reasons.append('4H timeframe')
    elif timeframe in ['1H', '60']:
        score += 5
        reasons.append('1H timeframe')
    elif timeframe in ['1', '5', '15', '30', '1M', '5M', '15M', '30M']:
        score -= 5
        reasons.append('Lower timeframe')

    if risk.get('decision') == 'WATCH':
        score += 10
        reasons.append('Risk model accepted')
    elif risk.get('decision') == 'REJECT':
        score -= 40
        reasons.append('Risk model rejected')

    if risk.get('risk_level') == 'medium':
        score += 5
        reasons.append('Risk level acceptable')
    elif risk.get('risk_level') == 'invalid':
        score -= 30
        reasons.append('Invalid risk profile')

    ai_decision = str(ai.get('decision', '')).lower()
    ai_confidence = ai.get('confidence')

    if ai_decision == 'pass':
        score += 10
        reasons.append('AI layer passed signal')
    elif ai_decision == 'reject':
        score -= 25
        reasons.append('AI layer rejected or downgraded signal')
    elif ai_decision == 'not_analyzed':
        score += 0
        reasons.append('AI not analyzed')

    if isinstance(ai_confidence, int):
        if ai_confidence >= 80:
            score += 5
            reasons.append('AI confidence high')
        elif ai_confidence < 50:
            score -= 10
            reasons.append('AI confidence low')

    score = max(0, min(100, score))
    if score >= 85:
        decision = 'STRONG_WATCH'
    elif score >= 70:
        decision = 'WATCH'
    elif score >= 55:
        decision = 'WEAK_WATCH'
    else:
        decision = 'IGNORE'

    return {'score': score, 'decision': decision, 'reasons': reasons}
