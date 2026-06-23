from fastapi import APIRouter

router = APIRouter(prefix="/mind-trader/bulk-capability", tags=["mind-trader"])

@router.get("/health")
def health():
    return {
        "ok": True,
        "status": "stub_active",
        "module": "mind_trader_bulk_capability_control"
    }
