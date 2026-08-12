import csv
from mind_trader.app.cli.status_cli import operational_status, run_status_cli, latest_reports
from mind_trader.app.risk.ftmo_ruleset import save_default_ftmo_config

def test_operational_status_basic():
    r=operational_status(tests_passed=201)
    assert r["decision"]=="STATUS_ONLY"
    assert r["production"]=="BLOCKED"
    assert r["live"]=="FORBIDDEN"
    assert r["edge_claim"]=="NONE"
    assert r["preflight"] is None

def test_operational_status_with_preflight(tmp_path):
    folder=tmp_path/"data"; folder.mkdir()
    with open(folder/"x.csv","w",encoding="utf-8",newline="") as f:
        w=csv.writer(f)
        w.writerow(["ts","open","high","low","close","volume"])
        w.writerow(["2026-01-01T09:00:00",1,2,0.5,1.5,100])
    cfg=tmp_path/"ftmo.json"; save_default_ftmo_config(str(cfg))
    r=operational_status(str(folder),str(cfg),201)
    assert r["preflight"]["decision"]=="PREFLIGHT_OK"

def test_status_cli_runs():
    r=run_status_cli(["--tests-passed","201"])
    assert r["decision"]=="STATUS_ONLY"

def test_latest_reports_returns_list():
    assert isinstance(latest_reports(),list)
