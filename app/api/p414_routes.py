from fastapi import APIRouter
from app.runtime.canary_gate import canary_health
router = APIRouter()

@router.get("/health/p414")
def p414_health():
    return canary_health()
