from app.runtime.cognitive_pipeline import run_cognitive_pipeline

def test_how_are_you():
    out = run_cognitive_pipeline("RobertoHuman", "como ta?")["answer"].lower()
    assert "funcionando bem" in out
    assert "me manda a pergunta de novo" not in out

def test_all_good():
    out = run_cognitive_pipeline("RobertoHuman", "tudo bem?")["answer"].lower()
    assert "natural" in out or "funcionando bem" in out
    assert "me manda a pergunta de novo" not in out

def test_good_afternoon():
    out = run_cognitive_pipeline("RobertoHuman", "boa tarde")["answer"].lower()
    assert "boa tarde" in out
    assert "contexto" in out
