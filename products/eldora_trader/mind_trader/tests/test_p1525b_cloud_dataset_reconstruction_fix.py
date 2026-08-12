from app.p1525b_cloud_dataset_reconstruction_fix.engine import metrics, corr, run

def test_p1525b_metrics():
    m=metrics([{"return":0.1},{"return":-0.02},{"return":0.03}],[1,1.1,1.078,1.11])
    assert "profit_factor" in m

def test_p1525b_corr():
    assert corr([1,2,3],[1,2,3]) >= 0.99

def test_p1525b_manifest():
    m=run()
    assert m["STATUS"]=="P15.25B_CLOUD_DATASET_RECONSTRUCTION_FIX_IMPLEMENTED"
    assert m["REAL_ORDERS"]=="FORBIDDEN"
    assert m["EXPORT_READY"] is True
