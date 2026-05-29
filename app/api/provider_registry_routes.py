from fastapi import APIRouter
from app.runtime.ai_provider_registry import provider_registry_status
from app.runtime.multi_provider_factual_provider import multi_provider_factual_provider

router = APIRouter()

@router.get("/providers/status")
def providers_status():
    return provider_registry_status()

@router.post("/providers/test")
def providers_test(payload: dict):
    return multi_provider_factual_provider(
        payload.get("message","teste"),
        payload.get("sender_id","debug"),
        payload.get("context",{})
    )
