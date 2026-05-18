from app.eldora.core.capability_synthesis_engine import synthesize_capability
from app.eldora.core.dynamic_skill_engine import generate_skill
from app.eldora.core.autonomous_capability_evolution import evolve_capability

def test_capability_synthesis():
    r=synthesize_capability("ocr_optimizer","improve multimodal ocr")
    assert r["status"]=="ok"

def test_dynamic_skill():
    r=generate_skill("semantic_ranker","retrieval")
    assert r["status"]=="ok"

def test_capability_evolution():
    r=evolve_capability("retrieval","improve ranking")
    assert r["status"]=="ok"
