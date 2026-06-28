import json

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from symbols import normalize_symbol, is_allowed_symbol
from utils import save_signal, now_utc
from ai import analyze_signal
from risk import analyze_risk
from scoring import score_signal

router = APIRouter()


@router.post("/webhook")
async def tradingview_webhook(request: Request):

    try:
        raw = (await request.body()).decode("utf-8")
        data = json.loads(raw)

        required = ["symbol", "price", "signal"]

        missing = [x for x in required if x not in data]

        if missing:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "Missing required fields",
                    "missing": missing,
                    "received": data,
                },
            )

        symbol = normalize_symbol(data["symbol"])

        if not is_allowed_symbol(symbol):
            return JSONResponse(
                status_code=403,
                content={
                    "status": "rejected",
                    "message": "Symbol not allowed",
                    "symbol": symbol,
                },
            )

        data["symbol"] = symbol
        data["signal"] = data["signal"].upper()

        saved = save_signal(data)

        ai_result = analyze_signal(saved)

        risk_result = analyze_risk(saved)

        score_result = score_signal(
            saved,
            risk_result,
            ai_result,
        )

        print("=" * 70)
        print("NEW SIGNAL RECEIVED")
        print(json.dumps(saved, indent=2))
        print("=" * 70)

        return {
            "status": "success",
            "message": "Duplicate ignored"
            if saved["is_duplicate"]
            else "Signal saved",

            "signal": saved,

            "ai": ai_result,

            "risk": risk_result,

            "score": score_result,
        }

    except json.JSONDecodeError:

        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": "Invalid JSON",
            },
        )

    except Exception as e:

        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(e),
            },
        )


@router.get("/webhook")
def webhook_status():

    return {
        "status": "online",
        "endpoint": "/webhook",
        "method": "POST",
        "message": "TradingView Webhook Ready",
    }


@router.get("/test-webhook")
def test_webhook():

    test_signal = {
        "symbol": "BTCUSD",
        "price": "65000",
        "time": now_utc(),
        "signal": "BUY",
        "timeframe": "1D",
        "exchange": "BITSTAMP",
        "volume": "1000",
    }

    saved = save_signal(
        test_signal,
        status="test_received",
    )

    ai_result = analyze_signal(saved)

    risk_result = analyze_risk(saved)

    score_result = score_signal(
        saved,
        risk_result,
        ai_result,
    )

    return {

        "status": "success",

        "message": "Test signal saved",

        "signal": saved,

        "ai": ai_result,

        "risk": risk_result,

        "score": score_result,
    }