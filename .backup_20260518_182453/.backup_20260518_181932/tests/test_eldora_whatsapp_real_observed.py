from app.runtime.cognitive_pipeline import run_cognitive_pipeline

def test_live_identity_no_old_fallback():
    out = run_cognitive_pipeline("RobertoLiveReal", "quem eh vc?")["answer"].lower()
    assert "eldora" in out
    assert "mind" in out
    assert "foco agora é melhorar" not in out

def test_live_what_are_you_doing_no_generic_retry():
    out = run_cognitive_pipeline("RobertoLiveReal", "que ta fazendo?")["answer"].lower()
    assert "ajustando" in out or "responder direto" in out or "contexto" in out
    assert "me manda a pergunta de novo" not in out

def test_live_how_no_generic_retry():
    out = run_cognitive_pipeline("RobertoLiveReal", "como?")["answer"].lower()
    assert "me manda a pergunta de novo" not in out
