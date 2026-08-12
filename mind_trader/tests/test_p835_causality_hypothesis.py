import csv, math
from pathlib import Path
from mind_trader.app.backtest.market_core import ingest_ohlcv_csv, load_ohlcv
from mind_trader.app.engines.causality_hypothesis import multi_lag_scan, causality_hypothesis_from_scan, causal_report, veto_edge_if_causality_unproven, save_causal_report

def write_leadlag(path, mode):
    vals=[]
    for i in range(160):
        base=math.sin(i/6)*0.5 + i*0.01
        if mode=="LEADER": vals.append(100+base)
        if mode=="FOLLOWER": vals.append(100+(math.sin((i-2)/6)*0.5 + max(i-2,0)*0.01))
    with open(path,"w",encoding="utf-8",newline="") as f:
        w=csv.writer(f); w.writerow(["ts","open","high","low","close","volume"])
        for i,p in enumerate(vals):
            w.writerow([f"2026-01-01T{i//60+9:02d}:{i%60:02d}:00",p-0.1,p+0.2,p-0.2,p,1000+i])

def seed(tmp_path):
    dbp=tmp_path/"m.sqlite"
    for s,m in [("LEAD","LEADER"),("FOLLOW","FOLLOWER")]:
        p=tmp_path/f"{s}.csv"; write_leadlag(p,m); ingest_ohlcv_csv(p,s,"1m",str(dbp))
    return dbp

def test_multi_lag_scan_runs(tmp_path):
    dbp=seed(tmp_path)
    a=load_ohlcv("LEAD","1m",str(dbp)); b=load_ohlcv("FOLLOW","1m",str(dbp))
    scan=multi_lag_scan(a,b,5)
    assert len(scan)==5
    assert "a_leads_b_corr" in scan[0]

def test_causality_hypothesis_never_claims_proven(tmp_path):
    dbp=seed(tmp_path)
    r=causal_report("LEAD","FOLLOW","1m",str(dbp),5)
    assert r["causality_claim"]=="NOT_PROVEN"
    assert r["edge_claim"]=="NONE"
    assert r["production"]=="BLOCKED"

def test_veto_edge_when_causality_not_proven():
    causal={"causality_claim":"NOT_PROVEN"}
    r=veto_edge_if_causality_unproven({"edge":"candidate"},causal)
    assert r["allowed"] is False
    assert r["decision"]=="VETO_EDGE_CAUSALITY_NOT_PROVEN"

def test_empty_scan_insufficient_data():
    r=causality_hypothesis_from_scan("A","B",[])
    assert r["hypothesis_strength"]=="INSUFFICIENT_DATA"
    assert r["production"]=="BLOCKED"

def test_save_causal_report(tmp_path):
    out=save_causal_report({"ok":True},str(tmp_path/"causal.json"))
    assert Path(out).exists()
