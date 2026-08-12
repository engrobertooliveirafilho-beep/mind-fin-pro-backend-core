from app.p1416a_risk_syntax_ladder.runner import run, EXPORT_DIR, TEMPLATES

def test_p1416a_generates_risk_ladder():
    m = run()
    assert m["STATUS"] == "P14.16A_RISK_SYNTAX_LADDER_IMPLEMENTED"
    assert m["REAL_ORDERS"] == "FORBIDDEN"
    assert m["EDGE"] == "NOT_PROVEN"
    for name in TEMPLATES:
        assert (EXPORT_DIR / f"{name}.nts").exists()

def test_p1416a_has_risk_probes():
    run()
    code = (EXPORT_DIR / "p1416a_l4_stop_take_probe.nts").read_text(encoding="utf-8")
    assert "SellToCoverStop" in code
    assert "BuyToCoverStop" in code
    assert "SellToCoverLimit" in code
    assert "BuyToCoverLimit" in code
