from fastapi import APIRouter
import os, socket
from datetime import datetime, timezone

router = APIRouter()

@router.get("/build_id")
def build_id():
    return {
        "status": "ok",
        "service": os.getenv("RENDER_SERVICE_NAME", "mind-fin-pro-backend"),
        "build_id": os.getenv("BUILD_ID") or os.getenv("RENDER_GIT_COMMIT") or "dev-local",
        "git_commit": os.getenv("RENDER_GIT_COMMIT", ""),
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "hostname": socket.gethostname()
    }

@router.get("/version")
def version():
    return build_id()
