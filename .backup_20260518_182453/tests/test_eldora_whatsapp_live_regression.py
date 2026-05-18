from app.runtime.cognitive_pipeline import run_cognitive_pipeline

def test_whatsapp_frustration_not_generic():
    out = run_cognitive_pipeline("RobertoLive", "mas nao ta funcionando")["answer"].lower()
    assert "você tem razão" in out or "voce tem razao" in out
    assert "frase genérica" in out or "frase generica" in out
    assert "foco agora é melhorar" not in out

def test_ambiguous_followup_not_generic():
    out = run_cognitive_pipeline("RobertoLive", "qual seria?")["answer"].lower()
    assert "gargalo" in out
    assert "memória curta" in out or "memoria curta" in out
    assert "foco agora é melhorar" not in out
