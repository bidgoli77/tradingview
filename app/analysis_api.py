import json
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.ai import analyze_signal
from app.risk import analyze_risk
from app.scoring import score_signal
from app.utils import get_signal_by_id, get_latest_signal

router = APIRouter()


def _decode_json_field(row: dict, field: str) -> dict:
    try:
        return json.loads(row.get(field) or '{}')
    except Exception:
        return {}


@router.get('/analysis/latest')
def latest_analysis(symbol: str | None = None):
    row = get_latest_signal(symbol)
    if not row:
        return JSONResponse(status_code=404, content={'status': 'not_found', 'message': 'No signal found'})

    risk = _decode_json_field(row, 'risk_json') or analyze_risk(row)
    ai = _decode_json_field(row, 'ai_json') or analyze_signal(row, risk)
    score = _decode_json_field(row, 'score_json') or score_signal(row, risk, ai)

    return {
        'status': 'success',
        'signal': row,
        'ai': ai,
        'risk': risk,
        'score': score,
    }


@router.get('/analysis/{signal_id}')
def signal_analysis(signal_id: int):
    row = get_signal_by_id(signal_id)
    if not row:
        return JSONResponse(status_code=404, content={'status': 'not_found', 'message': 'Signal not found'})

    risk = _decode_json_field(row, 'risk_json') or analyze_risk(row)
    ai = _decode_json_field(row, 'ai_json') or analyze_signal(row, risk)
    score = _decode_json_field(row, 'score_json') or score_signal(row, risk, ai)

    return {
        'status': 'success',
        'signal': row,
        'ai': ai,
        'risk': risk,
        'score': score,
    }
