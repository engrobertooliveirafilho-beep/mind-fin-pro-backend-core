import csv, math
from pathlib import Path
from mind_trader.app.backtest.market_core import ingest_ohlcv_csv
from mind_trader.app.engines.correlation_authority import correlation_authority_pair, correlation_matrix_authority, classify_relation, confidence_from_sample

def write_asset(path, mode):
    p=100
    with open(path,"w",encoding="utf-8",newline="") as f:
        w=csv.writer(f)
        w.writerow(["ts","open","high","low","close","volume"])
        for i in range(160):
            base=math.sin(i/8)*0.3+0.05
            p += base if mode=="A" else base*0.95
            w.writerow([f"2026-01-01T{i//60+9:02d}:{i%60:02d}:00",p-0.1,p+0.2,p-0.2,p,1000+i])

def seed(tmp_path):
    dbp=tmp_path/"m.sqlite"
    for s,m in [("AAA","A"),("BBB","B")]:
        p=tmp_path/f"{s}.csv"
        write_asset(p,m)
        ingest_ohlcv_csv(p,s,"1m",str(dbp))
    return dbp

def test_confidence_from_sample():
    assert confidence_from_sample(600)=="HIGH"
    assert confidence_from_sample(10)=="INSUFFICIENT"

def test_classify_relation():
    assert classify_relation(0.8)=="STRONG_POSITIVE"
    assert classify_relation(-0.8)=="STRONG_NEGATIVE"

def test_correlation_authority_pair(tmp_path):
    dbp=seed(tmp_path)
    r=correlation_authority_pair("AAA","BBB","1m",str(dbp))
    assert r["decision"]=="CORRELATION_RESEARCH_ONLY"
    assert r["production"]=="BLOCKED"
    assert r["edge_claim"]=="NONE"
    assert r["causality_claim"]=="NOT_PROVEN"

def test_correlation_matrix_authority(tmp_path):
    dbp=seed(tmp_path)
    r=correlation_matrix_authority(["AAA","BBB"],"1m",str(dbp))
    assert r["decision"]=="CORRELATION_MATRIX_RESEARCH_ONLY"
    assert len(r["pairs"])==1
    assert Path("mind_trader/reports/P8.76_correlation_authority.json").exists()
