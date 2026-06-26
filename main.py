from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from datetime import datetime

app = FastAPI()

latest_alert = {}
alert_history = []


@app.get("/", response_class=HTMLResponse)
def home():
    rows = ""

    for alert in reversed(alert_history[-20:]):
        rows += f"""
        <tr>
            <td>{alert.get("received_at", "-")}</td>
            <td>{alert.get("exchange", "-")}</td>
            <td>{alert.get("symbol", "-")}</td>
            <td>{alert.get("timeframe", "-")}</td>
            <td>{alert.get("price", "-")}</td>
            <td>{alert.get("volume", "-")}</td>
            <td>{alert.get("time", "-")}</td>
            <td>{alert.get("signal", "-")}</td>
        </tr>
        """

    return f"""
    <html>
    <body>
        <h2>TSX AI Webhook is running ✅</h2>

        <h3>Latest Alert</h3>
        <p><b>Exchange:</b> {latest_alert.get("exchange", "-")}</p>
        <p><b>Symbol:</b> {latest_alert.get("symbol", "-")}</p>
        <p><b>Timeframe:</b> {latest_alert.get("timeframe", "-")}</p>
        <p><b>Price:</b> {latest_alert.get("price", "-")}</p>
        <p><b>Volume:</b> {latest_alert.get("volume", "-")}</p>
        <p><b>TradingView Time:</b> {latest_alert.get("time", "-")}</p>
        <p><b>Signal:</b> {latest_alert.get("signal", "-")}</p>
        <p><b>Received At:</b> {latest_alert.get("received_at", "-")}</p>

        <h3>Last 20 Alerts</h3>
        <table border="1" cellpadding="8">
            <tr>
                <th>Received At</th>
                <th>Exchange</th>
                <th>Symbol</th>
                <th>Timeframe</th>
                <th>Price</th>
                <th>Volume</th>
                <th>TradingView Time</th>
                <th>Signal</th>
            </tr>
            {rows}
        </table>
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
    global latest_alert, alert_history

    body = await request.body()

    try:
        data = await request.json()

        normalized_data = {
            "symbol": data.get("symbol", "-"),
            "price": data.get("price", "-"),
            "time": data.get("time", "-"),
            "signal": data.get("signal", "-"),
            "timeframe": data.get("timeframe", "-"),
            "exchange": data.get("exchange", "-"),
            "volume": data.get("volume", "-"),
            "received_at": datetime.utcnow().isoformat() + "Z"
        }

        latest_alert = normalized_data
        alert_history.append(normalized_data)
        alert_history = alert_history[-20:]

        print("Webhook received:", normalized_data)

        return {
            "status": "received",
            "data": normalized_data
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