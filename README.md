# Mehdi Trading Bot v3.3 — Google GenAI SDK

This version migrates the AI Signal Engine from the deprecated `google-generativeai` package to the new official `google-genai` SDK.

## Key changes

- Uses `from google import genai`
- Uses `client = genai.Client(api_key=GOOGLE_API_KEY)`
- Removes deprecated `google-generativeai`
- Adds `/debug-ai` endpoint for safe AI configuration diagnostics
- Keeps local deterministic fallback if Gemini fails

## Render Start Command

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

## Required Render Environment Variables

```env
ENABLE_AI_ANALYSIS=true
GOOGLE_API_KEY=YOUR_GOOGLE_AI_STUDIO_API_KEY
GEMINI_MODEL=gemini-1.5-flash
AI_MIN_SCORE_TO_PASS=60
AI_TIMEOUT_SECONDS=20
```

Do not put the real API key in GitHub. Add it only in Render → Environment.

## Test endpoints

```text
/health
/debug-ai
/test-webhook
/analysis/latest
/dashboard
```

Expected `/debug-ai` output:

```json
{
  "ai_enabled": true,
  "google_api_key_exists": true,
  "google_api_key_prefix": "AQ.Ab8RN",
  "gemini_model": "gemini-1.5-flash",
  "sdk": "google-genai"
}
```

Expected `/test-webhook` when Gemini succeeds:

```json
"ai": {
  "enabled": true,
  "provider": "google-genai"
}
```

If Gemini fails, the app will still return a safe local fallback and include the error string.
