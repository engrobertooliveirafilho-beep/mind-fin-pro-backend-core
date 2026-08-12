from app.runtime.knowledge_extraction_engine import extract_items
from app.runtime.capability_reconstruction_planner import plan_from_extraction

def test_p480_reconstruction_planner_creates_missions():
    extraction = extract_items(
        "p480_test",
        "Precisamos criar um engine de memória social. Isso ainda não foi implementado.",
        {"test": True}
    )
    plan = plan_from_extraction(extraction)
    assert plan["total_missions"] >= 1
