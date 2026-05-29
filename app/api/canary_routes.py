from fastapi import APIRouter
from app.runtime.canary_gate import canary_health

router = APIRouter()

@router.get("/health/canary")
def health_canary():
    return canary_health()
