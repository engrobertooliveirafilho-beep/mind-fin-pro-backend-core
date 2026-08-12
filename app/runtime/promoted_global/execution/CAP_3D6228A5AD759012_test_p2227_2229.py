from app.runtime.p2227_2229_advanced_layer import run

def test_advanced():
    r = run(20)
    assert r["status"] == "PASS"
    assert len(r["final_strategies"]) > 0
    assert "macro" in r["sample"][0]
