from app.eldora.core.multimodal_ingestion import extract_text
from app.eldora.core.ocr_engine import run_ocr_simulation
from app.eldora.core.audio_transcript_engine import transcript_audio_simulation
from app.eldora.core.visual_semantic_memory import store_visual_memory
from app.eldora.core.multimodal_fusion_engine import multimodal_fusion

def test_ocr():
    r=run_ocr_simulation("eldora visual cognition")
    assert r["status"]=="ok"

def test_audio():
    r=transcript_audio_simulation("teste de transcrição")
    assert r["status"]=="ok"

def test_visual_memory():
    r=store_visual_memory("gráfico financeiro")
    assert r["stored"] is True

def test_multimodal_fusion():
    r=multimodal_fusion("financeiro","imagem + áudio + texto")
    assert r["status"]=="ok"
