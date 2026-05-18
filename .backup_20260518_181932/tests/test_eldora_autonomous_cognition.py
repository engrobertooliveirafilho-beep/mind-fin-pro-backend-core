from app.api.eldora_autonomous_cognition import run

def test_autonomous_cognition_ready():
    out=run({"user_id":"Roberto","message":"prosseguir evolução do MIND"})
    assert out["STATUS_FINAL"]=="ELDORA_LONGITUDINAL_MEMORY_AUTONOMOUS_COGNITION_READY"
    assert out["memory"]["stored"] is True
    assert out["plan"]["priority"]=="P1"
    assert out["patterns"]["preferred_style"]
