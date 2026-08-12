import csv
from pathlib import Path
from app.p13_incremental_ingestion.engine import inspect_file, run

def make_csv(p, n=220):
    with open(p,"w",newline="",encoding="utf-8") as f:
        w=csv.writer(f); w.writerow(["time","open","high","low","close","volume"])
        for i in range(n):
            w.writerow([f"2026-01-01 00:{i%60:02d}",100+i,101+i,99+i,100.5+i,1000+i])

def test_p133_inspect_valid_csv(tmp_path):
    p=tmp_path/"x.csv"; make_csv(p)
    r=inspect_file(p)
    assert r["schema_ok"] is True
    assert r["status"]=="READY_FOR_CERTIFICATION"

def test_p133_run_manifest():
    m=run()
    assert m["STATUS"]=="P13.3_INCREMENTAL_INGESTION_IMPLEMENTED"
    assert m["LIVE"]=="FORBIDDEN"
    assert m["EXPORT_READY"] is True

def test_p133_report_written():
    run()
    assert Path("reports/P13.3_INCREMENTAL_INGESTION/P13.3_manifest.json").exists()
