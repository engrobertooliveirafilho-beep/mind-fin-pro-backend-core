from app.runtime.cognitive_pipeline import run_cognitive_pipeline

def test_followup_comparison():
    out = run_cognitive_pipeline("RobertoFollow", "qual o melhor?")["answer"]
    assert "conversa natural" in out.lower()
    assert "infraestrutura" in out.lower()

def test_followup_causal():
    run_cognitive_pipeline("RobertoCause", "qual o melhor?")
    out = run_cognitive_pipeline("RobertoCause", "porque?")["answer"]
    assert "porque" in out.lower()
    assert "gargalo" in out.lower()

def test_followup_confirmation():
    run_cognitive_pipeline("RobertoConfirm", "qual o melhor?")
    out = run_cognitive_pipeline("RobertoConfirm", "certeza?")["answer"]
    assert "confiança" in out.lower()
    assert "evidência" in out.lower()
