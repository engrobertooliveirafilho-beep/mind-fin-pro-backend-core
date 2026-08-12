from mind_trader.app.data.dataset_lineage import create_dataset_lineage, verify_lineage

def sample_dataset():
    return {"dataset_id":"ds1","symbol":"WIN","timeframe":"1m","status":"APPROVED_FOR_RESEARCH"}

def sample_manifest():
    return {"file_path":"raw.csv","file_checksum":"abc","db_path":"m.sqlite","ingestion_result":{"quality":{"rows":100,"quality_passed":True}}}

def test_create_lineage():
    r=create_dataset_lineage(sample_dataset(),sample_manifest())
    assert r["lineage"]=="P8.64_DATASET_LINEAGE"
    assert len(r["lineage_hash"])==64
    assert r["production"]=="BLOCKED"

def test_verify_lineage_ok():
    r=create_dataset_lineage(sample_dataset(),sample_manifest())
    v=verify_lineage(r)
    assert v["valid"] is True
    assert v["decision"]=="LINEAGE_OK"

def test_verify_lineage_tamper():
    r=create_dataset_lineage(sample_dataset(),sample_manifest())
    r["symbol"]="WDO"
    v=verify_lineage(r)
    assert v["valid"] is False
    assert v["decision"]=="LINEAGE_TAMPERED"
