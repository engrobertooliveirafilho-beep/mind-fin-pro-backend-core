from app.modules.usde_core.theorem_engine import TheoremEngine

def test_no_free_lunch():
    r=TheoremEngine().no_free_lunch(10,5)
    assert r["warning"] is True

def test_pac_learning():
    r=TheoremEngine().pac_learning(0.05,0.99)
    assert r["pac_valid"] is True

def test_theorem_evaluate():
    r=TheoremEngine().evaluate({
        "accuracy":0.99,
        "overfitting":0.1,
        "baseline_gain":0.2
    })

    assert "AUDIT_EXTREME_ACCURACY" in r["findings"]
