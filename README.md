# Mehdi Trading Bot v3.2 — AI Signal Engine

Production-ready FastAPI core for TradingView webhooks with dashboard, SQLite storage, symbol whitelist, duplicate protection, risk management, scoring, and an AI signal analysis layer.

## Main endpoints

- `/health`
- `/dashboard`
- `/webhook` POST
- `/test-webhook` GET
- `/signals`
- `/signals/latest`
- `/portfolio`
- `/analysis/latest`
- `/analysis/{signal_id}`

## Render Start Command

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

## AI Mode

By default, AI analysis uses a deterministic local fallback and does not call Gemini.
To enable Gemini, set these environment variables in Render:

```env
ENABLE_AI_ANALYSIS=true
GOOGLE_API_KEY=your_key_here
GEMINI_MODEL=gemini-1.5-flash
AI_MIN_SCORE_TO_PASS=60
```

## TradingView Message

Use this in the Alert message field for strategy order fills:

```text
{{strategy.order.alert_message}}
```

Webhook URL:

```text
https://YOUR-RENDER-APP.onrender.com/webhook
```
