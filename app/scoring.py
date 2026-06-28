def score_signal(signal: dict, risk: dict, ai: dict) -> dict:
    score = 50
    reasons = []
    side = str(signal.get('signal', '')).upper()
    timeframe = str(signal.get('timeframe', '')).upper()
    if signal.get('is_duplicate'):
        return {'score': 0, 'decision': 'IGNORE', 'reasons': ['Duplicate signal ignored']}
    if side in ['BUY', 'SELL']:
        score += 10; reasons.append('Valid signal direction')
    if timeframe in ['1D', 'D', '1W', 'W']:
        score += 15; reasons.append('Higher timeframe')
    elif timeframe in ['4H', '240']:
        score += 10; reasons.append('4H timeframe')
    elif timeframe in ['1H', '60']:
        score += 5; reasons.append('1H timeframe')
    if risk.get('decision') == 'WATCH':
        score += 10; reasons.append('Risk model accepted')
    if risk.get('risk_level') == 'medium':
        score += 5; reasons.append('Risk level acceptable')
    if ai.get('decision') in ['pass', 'not_analyzed']:
        score += 5; reasons.append('AI did not reject')
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
