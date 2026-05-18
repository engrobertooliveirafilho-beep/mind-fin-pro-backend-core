from fastapi import APIRouter
from app.medical_research.runtime import GlobalMedicalResearchRuntime

router=APIRouter()

@router.post("/admin/medical-research/snapshot")
def snapshot(payload:dict):

    topic=payload.get(
        "topic",
        "novos tratamentos para câncer"
    )

    return GlobalMedicalResearchRuntime().research_snapshot(topic)
