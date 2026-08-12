from app.modules.usde_core.auto_hypothesis_generator import AutoHypothesisGenerator

def test_auto_hypothesis_generation():
    h=AutoHypothesisGenerator().generate(
        {"events":100}
    )

    assert len(h)>0
    assert "hypothesis_id" in h[0]

def test_auto_hypothesis_sorted():
    h=AutoHypothesisGenerator().generate(
        {"events":100}
    )

    assert h[0]["priority"] >= h[-1]["priority"]
