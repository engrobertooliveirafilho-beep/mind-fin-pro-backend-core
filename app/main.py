from fastapi import FastAPI
from app.api.runpod_routes import router as runpod_router

app = FastAPI(
    title="Eldora Cloud Runtime",
    version="runpod-cloud-v1"
)

@app.get("/health")
def health():
    return {
        "ok": True,
        "service": "eldora-cloud-runtime",
        "status":"ok"
    }

app.include_router(runpod_router)

# P_APP_MAIN_REGISTER_WHATSAPP
try:
    from app.api.whatsapp import router as whatsapp_router
    app.include_router(whatsapp_router)
except Exception as e:
    print("WHATSAPP_ROUTER_REGISTER_FAIL", e)
# /P_APP_MAIN_REGISTER_WHATSAPP
