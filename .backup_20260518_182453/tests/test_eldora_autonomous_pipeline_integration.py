from app.runtime.cognitive_pipeline import run_cognitive_pipeline

def test_autonomous_layer_inside_pipeline():
    out = run_cognitive_pipeline("Roberto", "prosseguir evolução do MIND com autonomia")
    assert out["autonomous"]["autonomous_ready"] is True
    assert out["autonomous"]["plan"]["priority"] == "P1"
    assert out["scores"]["generic_response_score"] <= 0.10
