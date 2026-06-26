import os
from datetime import datetime
from typing import Dict, Any, List

import requests
import google.generativeai as genai
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI()

latest_alert: Dict[str, Any] = {}
alert_history: List[Dict[str, Any]] = []

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


TSX60_SYMBOLS = [
    "RY", "TD", "BMO", "BNS", "CM", "NA",
    "SHOP", "BCE", "T", "ENB", "TRP", "CNQ",
    "SU", "CVE", "IMO", "MFC", "SLF", "GWO",
    "CNR", "CP", "WCN", "ATD", "L", "MRU",
    "DOL", "CTC.A", "QSR", "MG", "IFC", "FFH",
    "POW", "BAM", "BN", "AEM", "ABX", "WPM",
    "NTR", "TECK.B", "FM", "K", "FNV", "CCO",
    "WSP", "GIB.A", "CSU", "DSG", "OTEX", "TRI",
    "FTS", "EMA", "AQN", "PPL", "KEY", "TOU",
    "ARX", "GIL", "SAP", "WN", "EMP.A", "RCI.B"
]


def analyze_with_ai(alert: Dict[str, Any]) -> str:
    if not GEMINI_API_KEY:
        return "AI analysis skipped: GEMINI_API_KEY is not configured."

    prompt = f"""
You are an AI trading analyst.

Analyze this TradingView alert for educational/research purposes only.
Do not provide guaranteed financial advice.

Alert data:
Symbol: {alert.get("symbol")}
Exchange: {alert.get("exchange")}
Price: {alert.get("price")}
Volume: {alert.get("volume")}
Timeframe: {alert.get("timeframe")}
Signal: {alert.get("signal")}
TradingView Time: {alert.get("time")}

Return:
1. Market interpretation
2. Buy/Sell/Hold view
3. Risk level
4. Possible stop loss logic
5. Possible target logic
6. Confidence score from 0 to 100
7. Short warning disclaimer
"""

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI analysis error: {str(e)}"


def send_telegram_message(text: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(
            url,
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": text[:3900],
                "parse_mode": "HTML"
            },
            timeout=10
        )
    except Exception as e:
        print("Telegram error:", e)


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
            <td>{alert.get("signal", "-")}</td>
        </tr>
        """

    ai_text = latest_alert.get("ai_analysis", "-").replace("\n", "<br>")

    return f"""
    <html>
    <body style="font-family: Arial; padding: 20px;">
        <h2>TSX AI Trading Webhook ✅</h2>

        <h3>Latest Alert</h3>
        <p><b>Exchange:</b> {latest_alert.get("exchange", "-")}</p>
        <p><b>Symbol:</b> {latest_alert.get("symbol", "-")}</p>
        <p><b>Timeframe:</b> {latest_alert.get("timeframe", "-")}</p>
        <p><b>Price:</b> {latest_alert.get("price", "-")}</p>
        <p><b>Volume:</b> {latest_alert.get("volume", "-")}</p>
        <p><b>Signal:</b> {latest_alert.get("signal", "-")}</p>
        <p><b>TradingView Time:</b> {latest_alert.get("time", "-")}</p>
        <p><b>Received At:</b> {latest_alert.get("received_at", "-")}</p>

        <h3>AI Analysis</h3>
        <div style="border:1px solid #ccc; padding:15px; background:#f7f7f7;">
            {ai_text}
        </div>

        <h3>Last 20 Alerts</h3>
        <table border="1" cellpadding="8">
            <tr>
                <th>Received At</th>
                <th>Exchange</th>
                <th>Symbol</th>
                <th>Timeframe</th>
                <th>Price</th>
                <th>Volume</th>
                <th>Signal</th>
            </tr>
            {rows}
        </table>

        <h3>TSX60 Scanner Status</h3>
        <p>TSX60 symbols loaded: {len(TSX60_SYMBOLS)}</p>
        <p>Automatic scanning requires a market data API.</p>
    </body>
    </html>
    """


@app.get("/webhook")
def webhook_status():
    return {
        "status": "webhook endpoint is active",
        "message": "Use POST requests from TradingView alerts."
    }


@app.get("/tsx60")
def tsx60_symbols():
    return {"count": len(TSX60_SYMBOLS), "symbols": TSX60_SYMBOLS}


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

        ai_analysis = analyze_with_ai(normalized_data)
        normalized_data["ai_analysis"] = ai_analysis

        latest_alert = normalized_data
        alert_history.append(normalized_data)
        alert_history = alert_history[-20:]

        telegram_text = f"""
<b>AI Trading Alert</b>

Symbol: {normalized_data.get("symbol")}
Exchange: {normalized_data.get("exchange")}
Signal: {normalized_data.get("signal")}
Price: {normalized_data.get("price")}
Timeframe: {normalized_data.get("timeframe")}
Volume: {normalized_data.get("volume")}

AI Analysis:
{ai_analysis}
"""
        send_telegram_message(telegram_text)

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