from fastapi import APIRouter
from app.medical_swarm.debate_engine import MedicalDebateEngine
from app.medical_swarm.evidence_sync import MedicalEvidenceSync

router=APIRouter()

@router.post("/admin/medical-swarm/debate")
def medical_debate(payload:dict):
    topic = payload.get("topic","sepse grave")
    return MedicalDebateEngine().run_debate(topic)

@router.post("/admin/medical-swarm/evidence")
def medical_evidence(payload:dict):
    topic = payload.get("topic","sepsis treatment guideline")
    return MedicalEvidenceSync().evidence_pack(topic)

@router.post("/admin/medical-swarm/full-validation")
def medical_full_validation(payload:dict):
    topic = payload.get("topic","sepse grave")
    debate = MedicalDebateEngine().run_debate(topic)
    evidence = MedicalEvidenceSync().evidence_pack(topic)
    return {
        "status":"MEDICAL_CONSENSUS_VALIDATION_OPERATIONAL",
        "topic":topic,
        "debate":debate,
        "evidence":evidence,
        "final_gate":"EDUCATIONAL_USE_ONLY_REQUIRES_HUMAN_MEDICAL_REVIEW"
    }
