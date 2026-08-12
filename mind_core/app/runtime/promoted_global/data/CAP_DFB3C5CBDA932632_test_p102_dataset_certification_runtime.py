from app.p10_dataset_certification_runtime.engine import certify_dataset, register_certification, run

def test_p102_certifies_clean_dataset():
    c=certify_dataset({"schema_ok":True,"rows":220,"timestamp_order":True,"duplicate_ratio":0,"missing_ratio":0,"ohlcv_consistency":True,"unique_closes":40,"volume_validity":True})
    assert c["certified"] is True
    assert c["live"]=="FORBIDDEN"

def test_p102_rejects_bad_dataset():
    c=certify_dataset({"schema_ok":False,"rows":10})
    assert c["certified"] is False
    assert c["status"]=="REJECTED_OR_PENDING_FIX"

def test_p102_manifest():
    m=run()
    assert m["STATUS"]=="P10.2_DATASET_CERTIFICATION_RUNTIME_IMPLEMENTED"
    assert m["EXPORT_READY"] is True
