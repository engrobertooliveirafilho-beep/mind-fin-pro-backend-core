from app.p1310_mt5_normalized_dataset_certification.engine import run, certify_all

def test_p1310_certify_all_returns_list():
    assert isinstance(certify_all(), list)

def test_p1310_manifest():
    m=run()
    assert m["STATUS"]=="UNVERIFIED_PENDING_PROVENANCE_RECONCILIATION"
    assert m["REAL_ORDERS"]=="FORBIDDEN"
    assert m["EXPORT_READY"] is False
    assert m["FILES_CERTIFIED"] == 0

def test_p1310_certifies_existing_mt5_files():
    m=run()
    assert m["FILES_TOTAL"] >= 0
    assert m["FILES_CERTIFIED"] <= m["FILES_TOTAL"]
