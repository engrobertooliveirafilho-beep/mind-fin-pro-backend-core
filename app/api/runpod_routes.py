from fastapi import APIRouter
from app.integrations.runpod_client import RunPodClient

router = APIRouter(prefix="/runpod", tags=["runpod"])

@router.get("/health")
def runpod_health():
    try:
        client = RunPodClient()
        return client.health()
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "type": type(e).__name__
        }

@router.post("/echo")
def runpod_echo(payload: dict):
    try:
        client = RunPodClient()
        message = payload.get("message","test")
        return client.echo(message)
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "type": type(e).__name__
        }
