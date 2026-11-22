"""Isolated PAPER-only HTTP integration; never mount in production automatically."""
from fastapi import APIRouter, HTTPException
from app.runtime.step497_498_mock_guard import (
    execute_paper_pipeline, execute_paper_briefing, MockDataBlocked
)
from recovered.finance_steps.step497_pipeline_engine_original import get_business_pipeline_snapshot

router = APIRouter(prefix="/paper/finance", tags=["paper-finance"])

@router.get("/pipeline")
def paper_pipeline():
    try:
        return execute_paper_pipeline(get_business_pipeline_snapshot)
    except MockDataBlocked:
        raise HTTPException(status_code=503, detail="PAPER_PIPELINE_NOT_CERTIFIED")

@router.get("/ceo-briefing")
def paper_ceo_briefing():
    # STEP498 original imports other unverified engines and its STEP497 dependency
    # is known to be mock. Do not import or execute the original CEO engine.
    raise HTTPException(status_code=503, detail="PAPER_CEO_DEPENDENCIES_NOT_CERTIFIED")
