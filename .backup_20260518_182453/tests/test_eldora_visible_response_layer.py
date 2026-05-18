from app.runtime.cognitive_pipeline import run_cognitive_pipeline

def test_visible_response_why():
    out = run_cognitive_pipeline("RobertoVisible1", "porque?")["answer"]
    assert "infraestrutura" in out.lower()
    assert "Vou responder diferente" not in out

def test_visible_response_best():
    out = run_cognitive_pipeline("RobertoVisible2", "qual a melhor?")["answer"]
    assert "melhor" in out.lower()
    assert "conversacional" in out.lower()

def test_visible_response_where_answer():
    out = run_cognitive_pipeline("RobertoVisible3", "cadê a resposta?")["answer"]
    assert "resposta direta" in out.lower()
    assert "Vou responder diferente" not in out
