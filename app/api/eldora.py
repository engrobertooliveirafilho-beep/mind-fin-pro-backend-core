from fastapi import APIRouter

router = APIRouter(prefix="/eldora")

@router.get("/health")
async def health():
return {"status":"ok","runtime":"eldora"}

@router.get("/modules")
async def modules():
return {"modules":"active"}
