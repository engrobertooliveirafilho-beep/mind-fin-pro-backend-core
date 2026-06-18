from fastapi import APIRouter, Query
from app.mind.p5_5l_executive_decision_api.api import ExecutiveDecisionAPI

router = APIRouter(prefix="/p55/bulls", tags=["P5.5 Bulls"])

@router.get("/status")
def p55_bulls_status():
    return {
        "status": "P5.5N_FASTAPI_ROUTES_READY",
        "system": "GLOBAL_BOVINE_SPORTS_GENETICS_INTELLIGENCE_SYSTEM",
        "routes": ["/p55/bulls/status", "/p55/bulls/ranking", "/p55/bulls/decision"]
    }

@router.get("/ranking")
def p55_bulls_ranking(limit: int = Query(10, ge=1, le=50)):
    api = ExecutiveDecisionAPI()
    return {
        "status": "P5.5_RANKING_READY",
        "limit": limit,
        "ranking": api.ranking(limit)
    }

@router.get("/decision")
def p55_bulls_decision(question_type: str = "global_valuation_ranking", limit: int = Query(5, ge=1, le=20)):
    api = ExecutiveDecisionAPI()
    return api.decide(question_type, limit)
