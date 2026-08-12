def test_bulk_capability_wiring_imports():
    from app.runtime.mind_trader_bulk_capability_wiring import run, health

    h = health()
    assert h["mode"] == "PAPER_ONLY"
    assert h["real_orders"] == "FORBIDDEN"
    assert h["ftmo_real"] == "FORBIDDEN"
    assert h["modules_total"] >= 1
    assert h["imports_ok"] == h["modules_total"]

    out = run({"source":"P2338X12","mode":"PAPER_ONLY"})
    assert out["mode"] == "PAPER_ONLY"
    assert out["real_orders"] == "FORBIDDEN"
    assert out["ftmo_real"] == "FORBIDDEN"
    assert out["imports_ok"] == out["modules_total"]
