import csv, math
from pathlib import Path
from mind_trader.app.backtest.market_core import ingest_ohlcv_csv
from mind_trader.app.orchestration.research_orchestrator import run_research_orchestrator

def seed(tmp_path):
    p=tmp_path/"ohlcv.csv"; dbp=tmp_path/"m.sqlite"
    with open(p,"w",encoding="utf-8",newline="") as f:
        w=csv.writer(f); w.writerow(["ts","open","high","low","close","volume"])
        price=100
        for i in range(180):
            price += math.sin(i/8)*0.3 + 0.05
            w.writerow([f"2026-01-01T{i//60+9:02d}:{i%60:02d}:00",price-0.1,price+0.3,price-0.3,price,1000+i])
    ingest_ohlcv_csv(p,"TEST","1m",str(dbp))
    return dbp

def test_orchestrator_runs_full_pipeline(tmp_path):
    dbp=seed(tmp_path)
    r=run_research_orchestrator(symbols=("TEST",),timeframes=("1m",),db_path=str(dbp),limit=5)
    assert r["decision"]=="RESEARCH_ORCHESTRATION_COMPLETE"
    assert r["production"]=="BLOCKED"
    assert r["live"]=="FORBIDDEN"
    assert r["edge_claim"]=="NONE"
    assert r["genomes_executed"]==5
    assert "run_id" in r
    assert "snapshot_hash" in r
    assert "ledger_hash" in r

def test_orchestrator_writes_report(tmp_path):
    dbp=seed(tmp_path)
    run_research_orchestrator(symbols=("TEST",),timeframes=("1m",),db_path=str(dbp),limit=3)
    assert Path("mind_trader/reports/P8.44_research_orchestrator_report.json").exists()

def test_orchestrator_committee_blocks_incomplete_evidence(tmp_path):
    dbp=seed(tmp_path)
    r=run_research_orchestrator(symbols=("TEST",),timeframes=("1m",),db_path=str(dbp),limit=3)
    assert r["committee"]["result"]["decision"] in ["REJECTED_EDGE","INCOMPLETE_EVIDENCE"]
    assert r["committee"]["production"]=="BLOCKED"
