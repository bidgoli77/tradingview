# Mehdi Trading Bot v3.1 Professional Dashboard

Deploy-ready FastAPI TradingView webhook engine.

## Features
- TradingView `/webhook`
- SQLite signal storage
- Duplicate protection
- 20-symbol whitelist for TradingView Essential
- Risk manager
- Scoring engine
- Portfolio / symbol status engine
- Professional HTML dashboard at `/dashboard`
- Signal management API

## Render
Start command:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

## Test URLs
- `/health`
- `/symbols`
- `/test-webhook`
- `/logs`
- `/dashboard`
- `/portfolio`
- `/symbol-status`
- `/signals`
- `/signals/latest`

## TradingView Alert Message

```text
{{strategy.order.alert_message}}
```

Webhook URL:

```text
https://YOUR-RENDER-APP.onrender.com/webhook
```
