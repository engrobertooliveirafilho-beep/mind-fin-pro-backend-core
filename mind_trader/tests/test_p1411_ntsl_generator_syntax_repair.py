from pathlib import Path
from app.p1411_ntsl_generator_syntax_repair.runner import run, NTSL_FILE

def test_p1411_generates_ntsl_file():
    m = run()
    assert m["STATUS"] == "P14.11_NTSL_GENERATOR_SYNTAX_REPAIR_IMPLEMENTED"
    assert m["REAL_ORDERS"] == "FORBIDDEN"
    assert m["EDGE"] == "NOT_PROVEN"
    assert NTSL_FILE.exists()

def test_p1411_ntsl_is_not_empty_begin_end_only():
    run()
    code = NTSL_FILE.read_text(encoding="utf-8")
    assert "begin" in code
    assert "end;" in code
    assert "BuyAtMarket" in code
    assert "SellShortAtMarket" in code
