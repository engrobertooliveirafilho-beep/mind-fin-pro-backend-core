from fastapi import APIRouter
from app.integrations.runpod_client import RunPodClient

router = APIRouter(prefix="/runpod", tags=["runpod"])

@router.get("/health")
def runpod_health():
    client = RunPodClient()
    return client.health()

@router.post("/echo")
def runpod_echo(payload: dict):
    client = RunPodClient()
    message = payload.get("message", "eldora render to runpod test")
    return client.echo(message)
