from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes_build import router as build_router
from app.routes.routes_mind_talk import router as mind_talk_router

app = FastAPI(title="mind-fin-pro-backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok", "service": "mind-fin-pro-backend"}

app.include_router(build_router)
app.include_router(mind_talk_router)

@app.get("/build-id")
def build_id():
    return {"build_id": "mind-fin-pro-backend-core-main"}

@app.get("/health/env")
def health_env():
    return {"status": "ok", "service": "mind-fin-pro-backend", "env": "render"}

