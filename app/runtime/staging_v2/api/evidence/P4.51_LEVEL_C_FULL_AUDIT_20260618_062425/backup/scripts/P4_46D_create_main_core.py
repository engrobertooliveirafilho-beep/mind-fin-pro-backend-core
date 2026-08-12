from pathlib import Path

Path("app/main_core.py").write_text("""
from fastapi import FastAPI

app = FastAPI(title="MIND Core Runtime", version="P4.46D")

try:
    from app.api.eldora import router as eldora_router
    app.include_router(eldora_router)
except Exception:
    pass

try:
    from app.api.whatsapp import router as whatsapp_router
    app.include_router(whatsapp_router)
except Exception:
    pass

try:
    from app.api.p414_routes import router as p414_router
    app.include_router(p414_router)
except Exception:
    pass

try:
    from app.api.canary_routes import router as canary_router
    app.include_router(canary_router)
except Exception:
    pass

try:
    from app.admin.public_runtime import router as public_runtime_router
    app.include_router(public_runtime_router)
except Exception:
    pass

@app.get("/core/health")
def core_health():
    return {"status": "ok", "runtime": "main_core", "version": "P4.46D"}
""".strip() + "\n", encoding="utf-8")

print("app/main_core.py created")
