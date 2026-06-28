import json
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.symbols import normalize_symbol, is_allowed_symbol
from app.utils import save_signal, now_utc
from app.ai import analyze_signal
from app.risk import analyze_risk
from app.scoring import score_signal
from app.broker import paper_execute
from app.telegram import notify_signal
from app.logger import log_event

router = APIRouter()


def _validate_payload(data: dict):
    required = ['symbol', 'price', 'signal']
    missing = [x for x in required if x not in data]
    if missing:
        return JSONResponse(
            status_code=400,
            content={
                'status': 'error',
                'message': 'Missing required fields',
                'missing': missing,
                'received': data,
            },
        )

    symbol = normalize_symbol(data.get('symbol'))
    if not is_allowed_symbol(symbol):
        return JSONResponse(
            status_code=403,
            content={
                'status': 'rejected',
                'message': 'Symbol not allowed',
                'symbol': data.get('symbol'),
                'normalized_symbol': symbol,
            },
        )
    return None


def _process_signal(data: dict, status: str):
    data['symbol'] = normalize_symbol(data.get('symbol'))
    data['signal'] = str(data.get('signal')).upper()

    temp = {
        'symbol': data['symbol'],
        'price': data.get('price'),
        'signal': data['signal'],
        'timeframe': data.get('timeframe'),
        'exchange': data.get('exchange'),
        'volume': data.get('volume'),
        'is_duplicate': False,
    }

    risk_result = analyze_risk(temp)
    ai_result = analyze_signal(temp, risk_result)
    score_result = score_signal(temp, risk_result, ai_result)

    saved = save_signal(
        data,
        status=status,
        risk=risk_result,
        ai=ai_result,
        score=score_result,
        decision=score_result.get('decision'),
    )

    if saved.get('is_duplicate'):
        risk_result = analyze_risk(saved)
        ai_result = analyze_signal(saved, risk_result)
        score_result = score_signal(saved, risk_result, ai_result)

    broker_result = paper_execute(saved, risk_result, score_result)
    telegram_result = notify_signal(saved, risk_result, score_result)

    return saved, ai_result, risk_result, score_result, broker_result, telegram_result


@router.post('/webhook')
async def tradingview_webhook(request: Request):
    try:
        raw = (await request.body()).decode('utf-8')
        data = json.loads(raw)

        error = _validate_payload(data)
        if error:
            return error

        saved, ai_result, risk_result, score_result, broker_result, telegram_result = _process_signal(data, status='received')
        log_event('NEW TRADINGVIEW SIGNAL' if not saved.get('is_duplicate') else 'DUPLICATE SIGNAL', saved)

        return {
            'status': 'success',
            'message': 'Duplicate ignored' if saved.get('is_duplicate') else 'Signal saved',
            'signal': saved,
            'ai': ai_result,
            'risk': risk_result,
            'score': score_result,
            'broker': broker_result,
            'telegram': telegram_result,
        }

    except json.JSONDecodeError:
        return JSONResponse(status_code=400, content={'status': 'error', 'message': 'Invalid JSON'})
    except Exception as e:
        return JSONResponse(status_code=500, content={'status': 'error', 'message': str(e)})


@router.get('/webhook')
def webhook_status():
    return {
        'status': 'online',
        'endpoint': '/webhook',
        'method': 'POST',
        'message': 'TradingView Webhook Ready',
    }


@router.get('/test-webhook')
def test_webhook():
    data = {
        'symbol': 'BTCUSD',
        'price': '65000',
        'time': now_utc(),
        'signal': 'BUY',
        'timeframe': '1D',
        'exchange': 'BITSTAMP',
        'volume': '1000',
    }
    saved, ai_result, risk_result, score_result, broker_result, telegram_result = _process_signal(data, status='test_received')
    return {
        'status': 'success',
        'message': 'Test signal processed',
        'signal': saved,
        'ai': ai_result,
        'risk': risk_result,
        'score': score_result,
        'broker': broker_result,
        'telegram': telegram_result,
    }


@router.post('/test-webhook')
async def test_webhook_post(request: Request):
    try:
        data = json.loads((await request.body()).decode('utf-8'))
        error = _validate_payload(data)
        if error:
            return error
        saved, ai_result, risk_result, score_result, broker_result, telegram_result = _process_signal(data, status='manual_test_received')
        return {
            'status': 'success',
            'message': 'Manual test signal processed',
            'signal': saved,
            'ai': ai_result,
            'risk': risk_result,
            'score': score_result,
            'broker': broker_result,
            'telegram': telegram_result,
        }
    except json.JSONDecodeError:
        return JSONResponse(status_code=400, content={'status': 'error', 'message': 'Invalid JSON'})
