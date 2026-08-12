from app.p1414_mass_inline_ntsl_export.runner import run, EXPORT_DIR

def test_p1414_generates_mass_inline_files():
    m = run()
    assert m["STATUS"] == "P14.14_MASS_INLINE_NTSL_EXPORT_IMPLEMENTED"
    assert m["COUNT"] > 0
    assert m["REAL_ORDERS"] == "FORBIDDEN"
    assert m["EDGE"] == "NOT_PROVEN"

def test_p1414_files_are_inline_only():
    m = run()
    for g in m["GENERATED"]:
        code = (EXPORT_DIR / g["file"]).read_text(encoding="utf-8")
        assert "Media(" in code
        assert "BuyAtMarket" in code
        assert "SellShortAtMarket" in code
        assert "input" not in code.lower()
        assert "var" not in code.lower()
        assert "Float" not in code
        assert "MediaExp" not in code
