from app.runtime.cognitive_pipeline import run_cognitive_pipeline

def test_natural_response_layer():
    out = run_cognitive_pipeline("Roberto", "prosseguir evolução do MIND")
    assert "Roberto" in out["answer"]
    assert "MIND" in out["answer"]
    assert out["scores"]["generic_response_score"] <= 0.10
