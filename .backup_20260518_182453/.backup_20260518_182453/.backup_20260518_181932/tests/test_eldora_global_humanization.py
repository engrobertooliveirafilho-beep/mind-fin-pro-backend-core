from app.runtime.cognitive_pipeline import run_cognitive_pipeline

def test_global_humanization_ok():
    out = run_cognitive_pipeline("Roberto", "ok")
    assert "Diagnóstico:" not in out["answer"]

def test_global_humanization_opinion():
    out = run_cognitive_pipeline("Roberto", "e o que vc achou disso?")
    assert "avanço real" in out["answer"]
    assert "Diagnóstico:" not in out["answer"]

def test_global_humanization_prosseguir():
    out = run_cognitive_pipeline("Roberto", "prosseguir")
    assert "MIND" in out["answer"]
    assert "Diagnóstico:" not in out["answer"]
