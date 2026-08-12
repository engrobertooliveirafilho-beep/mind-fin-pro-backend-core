from app.p1416c_risk_factory_50.runner import run, EXPORT_DIR

def test_p1416c_generates_variants():
    m = run()
    assert m["STATUS"] == "P14.16C_RISK_FACTORY_50_IMPLEMENTED"
    assert m["COUNT"] > 0
    assert m["REAL_ORDERS"] == "FORBIDDEN"
    assert m["EDGE"] == "NOT_PROVEN"

def test_p1416c_inline_only():
    m = run()
    for g in m["GENERATED"]:
        code = (EXPORT_DIR / g["file"]).read_text(encoding="utf-8")
        assert "Media(" in code
        assert "Close > Media" in code
        assert "input" not in code.lower()
        assert "var" not in code.lower()
        assert "Float" not in code
        assert "MediaExp" not in code
