from fastapi import APIRouter

from app.eldora.core.multimodal_ingestion import extract_text
from app.eldora.core.ocr_engine import run_ocr_simulation, ocr_report
from app.eldora.core.audio_transcript_engine import transcript_audio_simulation, transcript_report
from app.eldora.core.visual_semantic_memory import store_visual_memory, visual_memory_report
from app.eldora.core.multimodal_fusion_engine import multimodal_fusion, fusion_report

router = APIRouter(prefix="/eldora/multimodal", tags=["eldora-multimodal"])

@router.get("/upload")
async def upload(path:str):
    return extract_text(path)

@router.post("/ocr")
async def ocr(content:str):
    return run_ocr_simulation(content)

@router.post("/audio/transcript")
async def transcript(text:str):
    return transcript_audio_simulation(text)

@router.post("/visual/store")
async def visual(description:str):
    return store_visual_memory(description)

@router.post("/fusion/query")
async def fusion(query:str, context:str):
    return multimodal_fusion(query, context)

@router.get("/fusion/report")
async def fusion_runtime():
    return fusion_report()

@router.get("/ocr/report")
async def ocr_runtime():
    return ocr_report()

@router.get("/audio/report")
async def audio_runtime():
    return transcript_report()

@router.get("/visual/report")
async def visual_runtime():
    return visual_memory_report()
