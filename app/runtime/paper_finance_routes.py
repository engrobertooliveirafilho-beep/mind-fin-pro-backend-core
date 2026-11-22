"""Isolated PAPER-only routes. Never import unverified engines or mount in production."""
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/paper/finance", tags=["paper-finance"])

@router.get("/pipeline")
def paper_pipeline():
    # Original STEP497 is known to contain hardcoded mock metrics.
    # Reject without importing, constructing, or executing the engine.
    raise HTTPException(status_code=503, detail="PAPER_PIPELINE_NOT_CERTIFIED")

@router.get("/ceo-briefing")
def paper_ceo_briefing():
    # STEP498 depends on mock STEP493/495/496/497.
    raise HTTPException(status_code=503, detail="PAPER_CEO_DEPENDENCIES_NOT_CERTIFIED")
