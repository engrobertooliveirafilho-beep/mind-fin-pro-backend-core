from fastapi import FastAPI
from app.routes_build import router as build_router
from app.routes.routes_mind_talk import router as mind_talk_router

app = FastAPI(title="mind-fin-pro-backend")

@app.get("/health")
def health():
    return {"status": "ok", "service": "mind-fin-pro-backend"}

app.include_router(build_router)
app.include_router(mind_talk_router)
