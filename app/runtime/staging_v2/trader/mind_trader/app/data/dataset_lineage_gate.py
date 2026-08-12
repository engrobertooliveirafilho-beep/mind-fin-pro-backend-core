import json
from pathlib import Path
from mind_trader.app.data.data_catalog import require_dataset_approved
from mind_trader.app.data.dataset_lineage import verify_lineage

def require_dataset_with_lineage(dataset_id_value,catalog_path="mind_trader/reports/P8.61_data_catalog.json",lineage_path="mind_trader/reports/P8.64_dataset_lineage.json"):
    ds=require_dataset_approved(dataset_id_value,catalog_path)
    if not ds["allowed"]:
        return {"allowed":False,"decision":ds["decision"],"dataset_check":ds,"production":"BLOCKED","edge_claim":"NONE"}

    p=Path(lineage_path)
    if not p.exists():
        return {"allowed":False,"decision":"BLOCK_LINEAGE_NOT_FOUND","dataset_check":ds,"production":"BLOCKED","edge_claim":"NONE"}

    lineage=json.loads(p.read_text(encoding="utf-8"))
    if lineage.get("dataset_id")!=dataset_id_value:
        return {"allowed":False,"decision":"BLOCK_LINEAGE_DATASET_MISMATCH","dataset_check":ds,"lineage_dataset_id":lineage.get("dataset_id"),"production":"BLOCKED","edge_claim":"NONE"}

    v=verify_lineage(lineage)
    if not v["valid"]:
        return {"allowed":False,"decision":"BLOCK_LINEAGE_INVALID","lineage_check":v,"production":"BLOCKED","edge_claim":"NONE"}

    return {"allowed":True,"decision":"DATASET_AND_LINEAGE_OK","dataset_check":ds,"lineage_check":v,"production":"BLOCKED","edge_claim":"NONE"}
