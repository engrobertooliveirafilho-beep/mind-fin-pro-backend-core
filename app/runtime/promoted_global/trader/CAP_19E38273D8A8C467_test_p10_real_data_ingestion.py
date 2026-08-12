from pathlib import Path
import csv
from app.p10_real_data_ingestion.engine import inspect_csv, register_file, run_demo

def make_csv(p, n=220):
    with open(p,"w",newline="",encoding="utf-8") as f:
        w=csv.writer(f)
        w.writerow(["time","open","high","low","close","volume"])
        for i in range(n):
            w.writerow([f"2026-01-01 00:{i%60:02d}",100+i,101+i,99+i,100.5+i,1000+i])

def test_p10_inspect_certifies_valid_csv(tmp_path):
    p=tmp_path/"data.csv"; make_csv(p)
    r=inspect_csv(p)
    assert r["schema_ok"] is True
    assert r["certified"] is True

def test_p10_register_blocks_live(tmp_path):
    p=tmp_path/"data.csv"; make_csv(p)
    r=register_file(p,"MT5_CSV","WIN","M1")
    assert r["live"]=="FORBIDDEN"
    assert r["real_broker"]=="DISABLED"
    assert r["edge"]=="NOT_PROVEN"

def test_p10_manifest():
    m=run_demo()
    assert m["STATUS"]=="P10_REAL_DATA_INGESTION_ENGINE_IMPLEMENTED"
    assert m["EXPORT_READY"] is True
