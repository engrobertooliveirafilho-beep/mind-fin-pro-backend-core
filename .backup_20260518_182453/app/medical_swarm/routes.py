from fastapi import APIRouter
from app.medical_swarm.runtime import MedicalSwarmRuntime

router=APIRouter()

@router.post("/admin/medical-swarm/simulate")
def simulate(payload:dict):

    topic=payload.get(
        "topic",
        "infarto agudo do miocárdio"
    )

    return MedicalSwarmRuntime().simulate(topic)
