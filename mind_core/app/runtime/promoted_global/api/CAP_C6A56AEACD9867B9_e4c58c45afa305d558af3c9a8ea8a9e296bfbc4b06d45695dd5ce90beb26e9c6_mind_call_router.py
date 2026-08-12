from fastapi import APIRouter

router = APIRouter()

@router.get("/health", tags=["health"])
def health():
    return {"ok": True, "module": "mind_call_router", "ts_utc": "2026-02-05T23:07:28.1953934Z"}

@router.get("/ping", tags=["health"])
def ping():
    return {"ok": True}
