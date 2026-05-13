
from supabase import create_client
import os

SUPABASE_URL=os.getenv("SUPABASE_URL")
SUPABASE_KEY=os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase=None

if SUPABASE_URL and SUPABASE_KEY:
    supabase=create_client(SUPABASE_URL,SUPABASE_KEY)

    try:
        supabase.table("neura_memory").select("*").limit(1).execute()
    except:
        pass


def memory_insert(sender_id,message):
    if not supabase:
        return

    supabase.table("neura_memory").insert({
        "sender_id": sender_id,
        "message": message
    }).execute()


def memory_fetch(sender_id):
    if not supabase:
        return []

    r=supabase.table("neura_memory")\
        .select("*")\
        .eq("sender_id",sender_id)\
        .order("id",desc=False)\
        .limit(20)\
        .execute()

    return r.data if r.data else []


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







@app.post("/webhook/whatsapp")
async def whatsapp_webhook_alias(payload: dict):

    sender_id = payload.get("sender_id", "unknown")
    message = payload.get("message", "")

    memory_insert(sender_id, message)
    history = memory_fetch(sender_id)

    response = "NEURA WEBHOOK ONLINE"

    lower = message.lower()

    if "qual é meu nome" in lower or "qual e meu nome" in lower:
        for h in history:
            m = h.get("message","")
            if "meu nome é" in m.lower() or "meu nome e" in m.lower():
                response = m.split("é")[-1].strip()
                break

    elif "o que estou estudando" in lower:
        for h in history:
            m = h.get("message","")
            if "estou estudando" in m.lower():
                response = m
                break

    elif "quando é minha prova" in lower or "quando e minha prova" in lower:
        for h in history:
            m = h.get("message","")
            if "prova" in m.lower():
                response = m
                break

    return {
        "status": "ok",
        "response": response,
        "history_count": len(history),
        "echo": payload
    }

