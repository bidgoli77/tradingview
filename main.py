from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI()

latest_alert = {}

@app.get("/", response_class=HTMLResponse)
def home():
    symbol = latest_alert.get("symbol", "-")
    price = latest_alert.get("price", "-")
    time = latest_alert.get("time", "-")
    signal = latest_alert.get("signal", "-")
    timeframe = latest_alert.get("timeframe", "-")
    exchange = latest_alert.get("exchange", "-")
    volume = latest_alert.get("volume", "-")

    return f"""
    <html>
    <body>
        <h2>TSX AI Webhook is running ✅</h2>
        <h3>Latest Alert</h3>exchange
        <p><b>Symbol:</b> {symbol}</p>
        <p><b>Price:</b> {price}</p>
        <p><b>Time:</b> {time}</p>
        <p><b>Signal:</b> {signal}</p>
        <p><b>Signal:</b> {timeframe}</p>
        <p><b>Signal:</b> {exchange}</p>
        <p><b>Signal:</b> {volume}</p>
    </body>
    </html>
    """

@app.get("/webhook")
def webhook_status():
    return {
        "status": "webhook endpoint is active",
        "message": "Use POST requests from TradingView alerts."
    }

@app.post("/webhook")
async def tradingview_webhook(request: Request):
    global latest_alert

    body = await request.body()

    try:
        data = await request.json()
        latest_alert = data
        print("Webhook received:", data)
        return {"status": "received", "data": data}

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