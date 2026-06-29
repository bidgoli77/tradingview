import json
from typing import Any

from app.config import (
    ENABLE_AI_ANALYSIS,
    GOOGLE_API_KEY,
    GEMINI_MODEL,
    AI_MIN_SCORE_TO_PASS,
    AI_TIMEOUT_SECONDS,
)


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def heuristic_analysis(signal: dict, risk: dict | None = None) -> dict:
    """Deterministic fallback used when Gemini is disabled or unavailable."""
    risk = risk or {}
    side = str(signal.get('signal', '')).upper()
    tf = str(signal.get('timeframe', '')).upper()
    symbol = str(signal.get('symbol', '')).upper()
    price = _safe_float(signal.get('price'))

    confidence = 50
    reasons: list[str] = []

    if side in {'BUY', 'SELL'}:
        confidence += 10
        reasons.append('Valid BUY/SELL direction received from TradingView strategy.')
    else:
        confidence -= 30
        reasons.append('Invalid signal direction.')

    if tf in {'1D', 'D', '1W', 'W'}:
        confidence += 15
        reasons.append('Higher timeframe signal usually has better noise control.')
    elif tf in {'4H', '240'}:
        confidence += 10
        reasons.append('4H timeframe is acceptable for swing-style signals.')
    elif tf in {'1H', '60'}:
        confidence += 5
        reasons.append('1H timeframe accepted, but noisier than daily/4H.')
    elif tf in {'1M', '5M', '15M', '30M', '1', '5', '15', '30'}:
        confidence -= 5
        reasons.append('Lower timeframe signal is noisier.')

    if risk.get('decision') == 'WATCH':
        confidence += 10
        reasons.append('Risk model accepted the signal.')
    if risk.get('risk_level') in {'low', 'medium'}:
        confidence += 5
        reasons.append('Risk level is acceptable.')
    if price <= 0:
        confidence -= 30
        reasons.append('Invalid or missing price.')

    confidence = max(0, min(100, confidence))
    decision = 'pass' if confidence >= AI_MIN_SCORE_TO_PASS else 'reject'

    return {
        'enabled': False,
        'provider': 'local_heuristic',
        'decision': decision,
        'confidence': confidence,
        'summary': f'{symbol} {side} signal reviewed by local deterministic fallback.',
        'reasons': reasons,
        'model': 'heuristic-v1',
    }


def _parse_json_object(text: str) -> dict:
    """Best-effort extraction of a JSON object from an LLM response."""
    text = (text or '').strip()
    if text.startswith('```'):
        text = text.strip('`')
        if text.lower().startswith('json'):
            text = text[4:].strip()
    start = text.find('{')
    end = text.rfind('}')
    if start >= 0 and end > start:
        text = text[start:end + 1]
    return json.loads(text)


def _gemini_analysis(signal: dict, risk: dict | None = None) -> dict:
    """Gemini analysis using the new official google-genai SDK."""
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=GOOGLE_API_KEY)

    prompt = f"""
You are a conservative trading-signal risk analyst. Review this TradingView signal and risk model.
Return ONLY valid JSON. Do not include markdown.

Signal:
{json.dumps(signal, ensure_ascii=False)}

Risk:
{json.dumps(risk or {}, ensure_ascii=False)}

Return this JSON schema exactly:
{{
  "decision": "pass" or "reject",
  "confidence": integer 0-100,
  "summary": "one short sentence",
  "reasons": ["reason 1", "reason 2"],
  "market_bias": "bullish" or "bearish" or "neutral",
  "risk_note": "one short risk note"
}}

Rules:
- Be conservative.
- Never claim certainty.
- Reject invalid price, invalid signal direction, or missing symbol.
- This is analysis only, not financial advice.
"""

    config = types.GenerateContentConfig(
        temperature=0.2,
        response_mime_type='application/json',
        max_output_tokens=800,
        http_options=types.HttpOptions(timeout=AI_TIMEOUT_SECONDS * 1000),
    )

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=config,
    )

    raw_text = getattr(response, 'text', '') or ''
    parsed = _parse_json_object(raw_text)

    decision = str(parsed.get('decision', 'reject')).lower()
    confidence = int(parsed.get('confidence', 0))
    confidence = max(0, min(100, confidence))
    if confidence < AI_MIN_SCORE_TO_PASS:
        decision = 'reject'

    return {
        'enabled': True,
        'provider': 'google-genai',
        'model': GEMINI_MODEL,
        'decision': decision,
        'confidence': confidence,
        'summary': parsed.get('summary', ''),
        'reasons': parsed.get('reasons', []),
        'market_bias': parsed.get('market_bias', 'neutral'),
        'risk_note': parsed.get('risk_note', ''),
    }


def analyze_signal(signal: dict, risk: dict | None = None) -> dict:
    """AI layer. Uses Gemini only when explicitly enabled; otherwise deterministic fallback."""
    if not ENABLE_AI_ANALYSIS:
        return heuristic_analysis(signal, risk)

    if not GOOGLE_API_KEY:
        result = heuristic_analysis(signal, risk)
        result['summary'] = 'AI enabled but GOOGLE_API_KEY/GEMINI_API_KEY missing; local fallback used.'
        return result

    try:
        return _gemini_analysis(signal, risk)
    except Exception as exc:
        result = heuristic_analysis(signal, risk)
        result['summary'] = 'Gemini failed; local fallback used.'
        result['error'] = str(exc)
        return result
