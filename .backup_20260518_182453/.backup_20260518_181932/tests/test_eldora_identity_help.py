from app.runtime.cognitive_pipeline import run_cognitive_pipeline

def test_identity_question():
    out = run_cognitive_pipeline("RobertoIdentity", "quem eh vc?")["answer"].lower()
    assert "eldora" in out
    assert "mind" in out
    assert "foco agora é melhorar" not in out

def test_help_question():
    out = run_cognitive_pipeline("RobertoIdentity", "como vai me ajudar?")["answer"].lower()
    assert "organizar" in out
    assert "contexto" in out
    assert "foco agora é melhorar" not in out
