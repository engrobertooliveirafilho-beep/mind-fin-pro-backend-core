from app.runtime.cognitive_pipeline import run_cognitive_pipeline

def test_cognitive_pipeline_for_whatsapp():
    out = run_cognitive_pipeline("whatsapp:+5511999999999", "Eldora, prosseguir evolução do MIND com memória e estratégia")
    assert out["scores"]["persona_consistency_score"] >= 0.90
    assert out["scores"]["context_continuity_score"] >= 0.90
    assert out["scores"]["generic_response_score"] <= 0.10
    assert "answer" in out
