from __future__ import annotations

from fastapi import APIRouter
from app.runtime.mind_trader_institutional_gate import health, run_gate

router = APIRouter(prefix="/mind-trader/institutional", tags=["mind-trader-institutional"])

@router.get("/health")
def institutional_health():
    return health()

@router.post("/run")
def institutional_run(payload: dict | None = None):
    return run_gate(payload or {})
