from app.config import ENABLE_AI_ANALYSIS, GOOGLE_API_KEY

def analyze_signal(signal: dict) -> dict:
    if not ENABLE_AI_ANALYSIS:
        return {'enabled': False, 'decision': 'not_analyzed', 'confidence': None, 'summary': 'AI analysis disabled'}
    if not GOOGLE_API_KEY:
        return {'enabled': False, 'decision': 'not_analyzed', 'confidence': None, 'summary': 'GOOGLE_API_KEY missing'}
    # v3.0 Core keeps Gemini integration as a safe placeholder.
    return {'enabled': True, 'decision': 'pass', 'confidence': 70, 'summary': 'Placeholder AI pass. Full Gemini analysis belongs to v3.2.'}
