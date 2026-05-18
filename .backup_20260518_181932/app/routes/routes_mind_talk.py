from fastapi import APIRouter

router = APIRouter()

@router.post("/mind/talk")
def mind_talk(payload: dict | None = None):
    return {
        "status": "ok",
        "message": "MIND TALK ONLINE",
        "echo": payload or {}
    }
