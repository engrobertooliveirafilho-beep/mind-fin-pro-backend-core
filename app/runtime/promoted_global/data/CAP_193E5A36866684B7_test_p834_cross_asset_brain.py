import csv, math
from pathlib import Path
from mind_trader.app.backtest.market_core import ingest_ohlcv_csv
from mind_trader.app.engines.cross_asset_brain import corr, cross_asset_report, matrix_report, lag_correlation, save_cross_asset_report

def write_asset(path, mode):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    prices=[]
    p=100
    for i in range(140):
        base=math.sin(i/8)
        if mode=="A": p+=base*0.3+0.05
        if mode=="B": p+=base*0.3+0.05
        if mode=="C": p-=base*0.3-0.02
        prices.append(p)
    with open(path,"w",encoding="utf-8",newline="") as f:
        w=csv.writer(f); w.writerow(["ts","open","high","low","close","volume"])
        for i,p in enumerate(prices):
            w.writerow([f"2026-01-01T{i//60+9:02d}:{i%60:02d}:00",p-0.1,p+0.2,p-0.2,p,1000+i])

def seed_db(tmp_path):
    dbp=tmp_path/"m.sqlite"
    for s,m in [("AAA","A"),("BBB","B"),("CCC","C")]:
        p=tmp_path/f"{s}.csv"; write_asset(p,m); ingest_ohlcv_csv(p,s,"1m",str(dbp))
    return dbp

def test_corr_basic():
    assert corr([1,2,3],[1,2,3]) > 0.99
    assert corr([1,2,3],[3,2,1]) < -0.99

def test_cross_asset_report_research_only(tmp_path):
    dbp=seed_db(tmp_path)
    r=cross_asset_report("AAA","BBB","1m",str(dbp))
    assert r["decision"]=="RESEARCH_HYPOTHESIS_ONLY"
    assert r["edge_claim"]=="NONE"
    assert r["production"]=="BLOCKED"
    assert r["causality_claim"]=="FORBIDDEN"

def test_matrix_report_count(tmp_path):
    dbp=seed_db(tmp_path)
    r=matrix_report(["AAA","BBB","CCC"],"1m",str(dbp))
    assert len(r)==3

def test_lag_correlation_has_sample(tmp_path):
    dbp=seed_db(tmp_path)
    from mind_trader.app.backtest.market_core import load_ohlcv
    a=load_ohlcv("AAA","1m",str(dbp)); b=load_ohlcv("BBB","1m",str(dbp))
    r=lag_correlation(a,b,1)
    assert r["sample_size"]>0

def test_insufficient_data_blocks():
    r=cross_asset_report("NONE","VOID","1m")
    assert r["decision"]=="INSUFFICIENT_DATA"

def test_save_cross_asset_report(tmp_path):
    out=save_cross_asset_report({"ok":True},str(tmp_path/"cross.json"))
    assert Path(out).exists()
