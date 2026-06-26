from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/")
def home():
    return {"status": "TSX AI Webhook is running"}

@app.get("/webhook")
def webhook_status():
    return {
        "status": "webhook endpoint is active",
        "message": "Use POST requests from TradingView alerts."
    }

@app.post("/webhook")
async def tradingview_webhook(request: Request):
    body = await request.body()

    try:
        data = await request.json()
        print("Webhook received:", data)
        return {
            "status": "received",
            "data": data
        }

    except Exception as e:
        raw_text = body.decode("utf-8", errors="ignore")
        print("Webhook raw body:", raw_text)
        return JSONResponse(
            status_code=200,
            content={
                "status": "received_raw",
                "raw": raw_text,
                "error": str(e)
            }
        )