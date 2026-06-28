
from config import ENABLE_AI_ANALYSIS, GOOGLE_API_KEY


def analyze_signal(signal: dict) -> dict:
    if not ENABLE_AI_ANALYSIS:
        return {
            "enabled": False,
            "decision": "not_analyzed",
            "reason": "AI analysis is disabled",
        }

    if not GOOGLE_API_KEY:
        return {
            "enabled": False,
            "decision": "not_analyzed",
            "reason": "GOOGLE_API_KEY is missing",
        }

    return {
        "enabled": True,
        "decision": "pass",
        "reason": "Placeholder AI filter. Full Gemini analysis will be added in next phase.",
    }