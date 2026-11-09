from app.p1515_web_research_to_backtest_queue.engine import certified_datasets, build_queue, run

def test_p1515_certified_datasets_list():
    assert certified_datasets() == []

def test_p1515_queue_builds():
    q = build_queue()
    assert q == []

def test_p1515_manifest_fails_closed_pending_canonical_reconciliation():
    m = run()
    assert m["STATUS"] == "BLOCKED_PENDING_CANONICAL_DATASET_RECONCILIATION"
    assert m["QUEUE_ITEMS"] == 0
    assert m["TOP_20"] == []
    assert m["REAL_ORDERS"] == "FORBIDDEN"
    assert m["REAL_BROKER"] == "DISABLED"
    assert m["LIVE"] == "FORBIDDEN"
    assert m["EXPORT_READY"] is False
    assert m["EDGE"] == "NOT_PROVEN_FOR_QUEUE"
    assert m["CAUSALITY"] == "NOT_PROVEN"
    assert m["NEXT"] == "RECONCILE_ORIGINAL_DATASET_MANIFESTS_BEFORE_BACKTEST"
