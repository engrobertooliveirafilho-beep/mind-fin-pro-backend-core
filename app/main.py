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
        "status": "render_boot_ok"
    }

app.include_router(runpod_router)
