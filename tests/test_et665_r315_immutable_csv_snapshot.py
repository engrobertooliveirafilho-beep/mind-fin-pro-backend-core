import hashlib
from mind_trader.research.et665_r315_immutable_csv_snapshot import snapshot_verified_csv

def test_snapshot_passes_but_never_promotes(tmp_path):
    p=tmp_path/"x.csv"
    p.write_text("edge_id,timestamp,pnl_r\nA,1,1\nB,1,2\n")
    r=snapshot_verified_csv(p,hashlib.sha256(p.read_bytes()).hexdigest())
    assert r["verified"] and len(r["rows"])==2
    assert r["runtime_promotion_allowed"] is False

def test_changed_bytes_rejected(tmp_path):
    p=tmp_path/"x.csv"
    p.write_text("edge_id,timestamp,pnl_r\nA,1,1\n")
    digest=hashlib.sha256(p.read_bytes()).hexdigest()
    p.write_text("edge_id,timestamp,pnl_r\nA,1,2\n")
    assert "SOURCE_HASH_MISMATCH" in snapshot_verified_csv(p,digest)["issues"]

def test_size_limit(tmp_path):
    p=tmp_path/"x.csv"
    p.write_text("edge_id,timestamp,pnl_r\nA,1,1\n")
    assert "SOURCE_TOO_LARGE" in snapshot_verified_csv(p,"0"*64,max_bytes=4)["issues"]

def test_symlink_rejected(tmp_path):
    p=tmp_path/"x.csv"
    p.write_text("edge_id,timestamp,pnl_r\nA,1,1\n")
    link=tmp_path/"alias.csv"
    link.symlink_to(p)
    assert "INVALID_SOURCE_PATH" in snapshot_verified_csv(link,"0"*64)["issues"]
