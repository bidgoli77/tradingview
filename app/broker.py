def paper_execute(signal: dict, risk: dict, score: dict) -> dict:
    # v3.0 Core never sends live orders.
    return {
        'mode': 'paper',
        'executed': False,
        'reason': 'Broker execution disabled in v3.0 Core',
        'suggested_action': score.get('decision')
    }
