from pathlib import Path
from app.p137_real_data_requirement_pack.engine import run, REQUIRED_DATASETS

def test_p137_required_datasets_exist():
    assert len(REQUIRED_DATASETS) >= 9
    assert any(x["asset"]=="WIN" for x in REQUIRED_DATASETS)
    assert any(x["asset"]=="AAPL" for x in REQUIRED_DATASETS)

def test_p137_manifest():
    m=run()
    assert m["STATUS"]=="P13.7_REAL_DATA_REQUIREMENT_PACK_IMPLEMENTED"
    assert m["EXPORT_READY"] is True

def test_p137_dirs_created():
    run()
    for row in REQUIRED_DATASETS:
        assert Path(row["target"]).parent.exists()
