def test_mind_trader_institutional_wiring_imports():
    from app.runtime.mind_trader_institutional_wiring import run, health

    h = health()
    assert isinstance(h, dict)
    assert h["modules_total"] == 10
    assert h["imports_ok"] == 10
    assert h["status"] in {"OK", "DEGRADED"}

    out = run({"mode": "PAPER_ONLY", "test": "P2338X7"})
    assert isinstance(out, dict)
    assert out["mode"] == "PAPER_ONLY"
    assert out["real_orders"] == "FORBIDDEN"
    assert out["ftmo_real"] == "FORBIDDEN"
    assert out["modules_total"] == 10
    assert out["imports_ok"] == 10
    assert "results" in out
    assert isinstance(out["results"], list)
