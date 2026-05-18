from fastapi import APIRouter
from app.multi_llm.provider_runtime import ProviderRuntime

router=APIRouter()

@router.get("/admin/multi-llm/providers/health")
def providers_health():
    return {"status":"PROVIDER_HEALTH_REPORT","providers":ProviderRuntime().health_report()}

@router.post("/admin/multi-llm/provider/test")
def provider_test(payload:dict):
    provider=payload.get("provider","openai")
    message=payload.get("message","responda em português: teste")
    try:
        return {"status":"PROVIDER_EXECUTION_OK","result":ProviderRuntime().execute(provider,message)}
    except Exception as e:
        return {"status":"PROVIDER_EXECUTION_FAILED","provider":provider,"error":str(e)}
