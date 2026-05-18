from app.runtime.cognitive_pipeline import run_cognitive_pipeline

def test_dialogue_not_repeat_sequence():
    a = run_cognitive_pipeline("Roberto", "oi")["answer"]
    b = run_cognitive_pipeline("Roberto", "e como posso fazer isso?")["answer"]
    c = run_cognitive_pipeline("Roberto", "porque vc repete?")["answer"]
    assert a != b
    assert b != c
    assert "template fixo" in c.lower() or "repetindo" in c.lower()

def test_short_ack_no_template():
    out = run_cognitive_pipeline("Roberto2", "ok")["answer"]
    assert "Diagnóstico:" not in out
    assert len(out) < 160
