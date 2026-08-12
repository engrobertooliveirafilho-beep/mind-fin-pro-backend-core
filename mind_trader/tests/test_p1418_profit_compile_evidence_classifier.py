from app.p1418_profit_compile_evidence_classifier.engine import classify_row, classify_all, run

def test_p1418_classify_missing_screenshot_reference():
    r=classify_row({"strategy_id":"x","screenshot":"missing.png"})
    assert r=="SCREENSHOT_REFERENCED_MISSING"

def test_p1418_classify_all_list():
    assert isinstance(classify_all(), list)

def test_p1418_manifest():
    m=run()
    assert m["STATUS"]=="P14.18_PROFIT_COMPILE_EVIDENCE_CLASSIFIER_IMPLEMENTED"
    assert m["REAL_ORDERS"]=="FORBIDDEN"
    assert m["EXPORT_READY"] is True
