from fastapi import APIRouter
from app.medical_curriculum.future_linker import MedicalCurriculumFutureLinker

router=APIRouter()

@router.post("/admin/medical-curriculum/future-link")
def future_link(payload:dict):
    return MedicalCurriculumFutureLinker().link(
        payload.get("subject","anatomia"),
        payload.get("topic","")
    )
