from app.p1413_inline_ntsl_generator_patch.runner import run, NTSL_FILE

def test_p1413_generates_inline_strategy():
    m = run()
    assert m["STATUS"] == "P14.13_INLINE_NTSL_GENERATOR_PATCH_IMPLEMENTED"
    assert m["REAL_ORDERS"] == "FORBIDDEN"
    assert m["EDGE"] == "NOT_PROVEN"
    assert NTSL_FILE.exists()

def test_p1413_avoids_unproven_blocks():
    run()
    code = NTSL_FILE.read_text(encoding="utf-8")
    assert "input" not in code.lower()
    assert "var" not in code.lower()
    assert "Float" not in code
    assert "Media(" in code
    assert "BuyAtMarket" in code
    assert "SellShortAtMarket" in code
