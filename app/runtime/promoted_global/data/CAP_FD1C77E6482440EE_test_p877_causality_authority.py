import csv, math
from pathlib import Path
from mind_trader.app.backtest.market_core import ingest_ohlcv_csv
from mind_trader.app.engines.causality_authority import causality_authority, placebo_lag_test, veto_if_causality_not_proven
from mind_trader.app.backtest.market_core import load_ohlcv

def write_asset(path, mode):
    vals=[]
    for i in range(170):
        base=math.sin(i/6)*0.5+i*0.01
        vals.append(100+base if mode=="LEAD" else 100+(math.sin((i-2)/6)*0.5+max(i-2,0)*0.01))
    with open(path,"w",encoding="utf-8",newline="") as f:
        w=csv.writer(f); w.writerow(["ts","open","high","low","close","volume"])
        for i,p in enumerate(vals):
            w.writerow([f"2026-01-01T{i//60+9:02d}:{i%60:02d}:00",p-0.1,p+0.2,p-0.2,p,1000+i])

def seed(tmp_path):
    dbp=tmp_path/"m.sqlite"
    for s,m in [("LEAD","LEAD"),("FOLLOW","FOLLOW")]:
        p=tmp_path/f"{s}.csv"; write_asset(p,m); ingest_ohlcv_csv(p,s,"1m",str(dbp))
    return dbp

def test_placebo_lag_test_runs(tmp_path):
    dbp=seed(tmp_path)
    a=load_ohlcv("LEAD","1m",str(dbp)); b=load_ohlcv("FOLLOW","1m",str(dbp))
    r=placebo_lag_test(a,b,runs=10)
    assert "passed" in r
    assert r["runs"]==10

def test_causality_authority_never_proves_causality(tmp_path):
    dbp=seed(tmp_path)
    r=causality_authority("LEAD","FOLLOW","1m",str(dbp))
    assert r["causality_claim"]=="NOT_PROVEN"
    assert r["edge_claim"]=="NONE"
    assert r["production"]=="BLOCKED"
    assert r["live"]=="FORBIDDEN"

def test_causality_report_written(tmp_path):
    dbp=seed(tmp_path)
    causality_authority("LEAD","FOLLOW","1m",str(dbp))
    assert Path("mind_trader/reports/P8.77_causality_authority.json").exists()

def test_veto_if_causality_not_proven():
    r=veto_if_causality_not_proven({"decision":"CAUSAL_RESEARCH_HYPOTHESIS","causality_claim":"NOT_PROVEN"})
    assert r["allowed"] is False
    assert r["decision"]=="VETO_CAUSALITY_NOT_PROVEN"
