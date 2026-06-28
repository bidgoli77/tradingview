from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
from datetime import datetime, timezone
import json
import os

app = FastAPI(title="Mehdi Trading Bot API")

SIGNALS = []


class Signal(BaseModel):
    symbol: str
    price: str | float
    time: str | None = None
    signal: str
    timeframe: str | None = None
    exchange: str | None = None
    volume: str | float | None = None


@app.get("/")
def home():
    return {
        "status": "online",
        "service": "Mehdi Trading Bot",
        "endpoints": ["/webhook", "/logs", "/health", "/test-webhook"],
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "time": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/webhook")
async def webhook(request: Request):
    try:
        body = await request.body()
        raw = body.decode("utf-8")

        data = json.loads(raw)

        required = ["symbol", "price", "signal"]
        missing = [k for k in required if k not in data]

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

        signal = {
            "id": len(SIGNALS) + 1,
            "received_at": datetime.now(timezone.utc).isoformat(),
            "symbol": data.get("symbol"),
            "price": data.get("price"),
            "time": data.get("time"),
            "signal": str(data.get("signal")).upper(),
            "timeframe": data.get("timeframe"),
            "exchange": data.get("exchange"),
            "volume": data.get("volume"),
            "status": "received",
        }

        SIGNALS.append(signal)

        print("✅ NEW SIGNAL RECEIVED:")
        print(json.dumps(signal, indent=2))

        return {
            "status": "success",
            "message": "Signal received",
            "signal": signal,
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


@app.get("/webhook")
def webhook_get():
    return {
        "status": "webhook endpoint is active",
        "method": "POST required",
    }


@app.get("/test-webhook")
def test_webhook():
    test_signal = {
        "id": len(SIGNALS) + 1,
        "received_at": datetime.now(timezone.utc).isoformat(),
        "symbol": "BTCUSD",
        "price": "65000",
        "time": datetime.now(timezone.utc).isoformat(),
        "signal": "BUY",
        "timeframe": "1D",
        "exchange": "BITSTAMP",
        "volume": "1000",
        "status": "test_received",
    }

    SIGNALS.append(test_signal)

    print("🧪 TEST SIGNAL:")
    print(json.dumps(test_signal, indent=2))

    return {
        "status": "success",
        "message": "Test signal created",
        "signal": test_signal,
    }


@app.get("/logs")
def logs():
    return {
        "total_signals": len(SIGNALS),
        "signals": SIGNALS[-50:],
    }