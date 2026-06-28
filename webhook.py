import json
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from risk import analyze_risk


from symbols import is_allowed_symbol, normalize_symbol
from utils import save_signal, now_utc
from ai import analyze_signal

router = APIRouter()


@router.post("/webhook")
async def tradingview_webhook(request: Request):
    try:
        raw = (await request.body()).decode("utf-8")
        data = json.loads(raw)

        required = ["symbol", "price", "signal"]
        missing = [field for field in required if field not in data]

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

        normalized_symbol = normalize_symbol(data.get("symbol"))

        if not is_allowed_symbol(normalized_symbol):
            return JSONResponse(
                status_code=403,
                content={
                    "status": "rejected",
                    "message": "Symbol not allowed",
                    "symbol": data.get("symbol"),
                    "normalized_symbol": normalized_symbol,
                },
            )

        data["symbol"] = normalized_symbol
        data["signal"] = str(data.get("signal")).upper()

        saved = save_signal(data)
        ai_result = analyze_signal(saved)
        risk_result = analyze_risk(saved)

        print("✅ NEW SIGNAL SAVED:" if not saved["is_duplicate"] else "⚠️ DUPLICATE SIGNAL IGNORED:")
        print(json.dumps(saved, indent=2))

        return {
            "status": "success",
            "message": "Duplicate ignored" if saved["is_duplicate"] else "Signal saved",
            "signal": saved,
            "ai": ai_result,
        }

    except json.JSONDecodeError:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "Invalid JSON"},
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)},
        )


@router.get("/webhook")
def webhook_status():
    return {
        "status": "active",
        "message": "Webhook endpoint is active. Use POST from TradingView.",
    }


@router.get("/test-webhook")
def test_webhook():
    test_data = {
        "symbol": "BTCUSD",
        "price": "65000",
        "time": now_utc(),
        "signal": "BUY",
        "timeframe": "1D",
        "exchange": "BITSTAMP",
        "volume": "1000",
    }

    saved = save_signal(test_data, status="test_received")

    return {
        "status": "success",
        "message": "Test signal saved",
        "signal": saved,
        "risk": risk_result,
    }