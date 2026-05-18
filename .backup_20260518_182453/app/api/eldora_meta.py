from fastapi import APIRouter

from app.eldora.core.meta_cognition_engine import (
    analyze_internal_state,
    meta_cognition_report
)

from app.eldora.core.self_awareness_engine import (
    self_awareness,
    awareness_report
)

from app.eldora.core.recursive_introspection_engine import (
    recursive_introspection,
    introspection_report
)

router = APIRouter(
    prefix="/eldora/meta",
    tags=["eldora-meta"]
)

@router.post("/cognition/analyze")
async def cognition(runtime:str, cognition:str):
    return analyze_internal_state(runtime, cognition)

@router.get("/cognition/report")
async def cognition_runtime():
    return meta_cognition_report()

@router.post("/awareness/analyze")
async def awareness(runtime_state:str, objective:str):
    return self_awareness(runtime_state, objective)

@router.get("/awareness/report")
async def awareness_runtime():
    return awareness_report()

@router.post("/introspection/run")
async def introspection(layer:str, reflection:str):
    return recursive_introspection(layer, reflection)

@router.get("/introspection/report")
async def introspection_runtime():
    return introspection_report()
