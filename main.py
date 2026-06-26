from fastapi import FastAPI, Request

app = FastAPI()

@app.get("/")
def home():
    return {"status": "TSX AI Webhook is running"}

@app.post("/webhook")
async def tradingview_webhook(request: Request):
    data = await request.json()
    print("Webhook received:", data)

    return {
        "status": "received",
        "data": data
    }
