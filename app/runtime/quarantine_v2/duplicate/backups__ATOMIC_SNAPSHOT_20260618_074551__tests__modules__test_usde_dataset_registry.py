from app.modules.usde_core.dataset_registry import DatasetRegistry

def test_dataset_registry():
    r=DatasetRegistry()
    d=r.register("dataset.csv",{"rows":100})

    assert "dataset_id" in d
    assert r.count() >= 1
