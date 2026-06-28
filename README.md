# Mehdi Trading Bot v3.0 Core

Deployable FastAPI core for TradingView webhook signals.

## Features
- TradingView webhook receiver
- 20-symbol whitelist for TradingView Essential plan
- SQLite persistence
- Duplicate detection
- Risk manager
- Scoring engine
- Portfolio/symbol status engine
- Basic HTML dashboard
- AI, Telegram, Broker, Backtest placeholders for future versions

## Local run
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Open:
- http://localhost:8000/health
- http://localhost:8000/test-webhook
- http://localhost:8000/logs
- http://localhost:8000/dashboard

## TradingView webhook
URL:
```text
https://YOUR-RENDER-APP.onrender.com/webhook
```
Message:
```text
{{strategy.order.alert_message}}
```

## Pine JSON example
```json
{"symbol":"{{ticker}}","price":"{{close}}","time":"{{time}}","signal":"BUY","timeframe":"{{interval}}","exchange":"{{exchange}}","volume":"{{volume}}"}
```
