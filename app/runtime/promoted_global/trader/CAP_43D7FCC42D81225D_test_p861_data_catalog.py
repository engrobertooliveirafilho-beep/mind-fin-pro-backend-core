from mind_trader.app.data.data_catalog import dataset_id, register_dataset, load_catalog, require_dataset_approved

def test_dataset_id_stable():
    assert dataset_id("WIN","1m","abc")==dataset_id("WIN","1m","abc")

def test_register_approved_dataset(tmp_path):
    p=tmp_path/"catalog.json"
    ds=register_dataset("WIN","1m","abc",100,True,str(p))
    assert ds["status"]=="APPROVED_FOR_RESEARCH"
    assert len(load_catalog(str(p)))==1

def test_register_blocks_low_rows(tmp_path):
    p=tmp_path/"catalog.json"
    ds=register_dataset("WIN","1m","abc",10,True,str(p))
    assert ds["status"]=="BLOCKED_DATASET"

def test_require_dataset_approved(tmp_path):
    p=tmp_path/"catalog.json"
    ds=register_dataset("WIN","1m","abc",100,True,str(p))
    r=require_dataset_approved(ds["dataset_id"],str(p))
    assert r["allowed"] is True
    assert r["decision"]=="DATASET_OK"

def test_require_dataset_missing_blocks(tmp_path):
    r=require_dataset_approved("missing",str(tmp_path/"catalog.json"))
    assert r["allowed"] is False
    assert r["decision"]=="BLOCK_DATASET_NOT_FOUND"
