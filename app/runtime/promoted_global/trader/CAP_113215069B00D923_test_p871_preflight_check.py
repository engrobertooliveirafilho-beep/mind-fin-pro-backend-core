import csv
from pathlib import Path
from mind_trader.app.audits.preflight_check import preflight_check
from mind_trader.app.risk.ftmo_ruleset import save_default_ftmo_config

def test_preflight_blocks_missing_folder(tmp_path):
    cfg=tmp_path/"ftmo.json"; save_default_ftmo_config(str(cfg))
    r=preflight_check(tmp_path/"missing",str(cfg),196)
    assert r["decision"]=="PREFLIGHT_BLOCKED"
    assert r["checks"]["data_folder_exists"] is False

def test_preflight_blocks_empty_folder(tmp_path):
    folder=tmp_path/"data"; folder.mkdir()
    cfg=tmp_path/"ftmo.json"; save_default_ftmo_config(str(cfg))
    r=preflight_check(folder,str(cfg),196)
    assert r["decision"]=="PREFLIGHT_BLOCKED"
    assert r["checks"]["csv_files_present"] is False

def test_preflight_ok(tmp_path):
    folder=tmp_path/"data"; folder.mkdir()
    with open(folder/"x.csv","w",encoding="utf-8",newline="") as f:
        w=csv.writer(f)
        w.writerow(["ts","open","high","low","close","volume"])
        w.writerow(["2026-01-01T09:00:00",1,2,0.5,1.5,100])
    cfg=tmp_path/"ftmo.json"; save_default_ftmo_config(str(cfg))
    r=preflight_check(folder,str(cfg),196)
    assert r["decision"]=="PREFLIGHT_OK"
    assert r["production"]=="BLOCKED"
    assert r["live"]=="FORBIDDEN"
