from app.runtime.p2224_2226_institutional_core import run

def test_core():
    r = run(10)
    assert r["status"] == "PASS"
    assert len(r["final_strategies"]) > 0
    assert "book" in r["log_sample"][0]
