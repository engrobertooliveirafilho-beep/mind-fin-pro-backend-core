from fastapi import APIRouter

from app.eldora.core.capability_synthesis_engine import (
    synthesize_capability,
    capability_report
)

from app.eldora.core.dynamic_skill_engine import (
    generate_skill,
    skill_report
)

from app.eldora.core.autonomous_capability_evolution import (
    evolve_capability,
    evolution_report
)

router = APIRouter(
    prefix="/eldora/evolution",
    tags=["eldora-evolution"]
)

@router.post("/capability/synthesize")
async def synthesize(name:str, objective:str):
    return synthesize_capability(name, objective)

@router.get("/capability/report")
async def capability_runtime():
    return capability_report()

@router.post("/skill/generate")
async def skill(skill_name:str, domain:str):
    return generate_skill(skill_name, domain)

@router.get("/skill/report")
async def skill_runtime():
    return skill_report()

@router.post("/capability/evolve")
async def evolve(capability:str, improvement:str):
    return evolve_capability(capability, improvement)

@router.get("/evolution/report")
async def evolution_runtime():
    return evolution_report()
