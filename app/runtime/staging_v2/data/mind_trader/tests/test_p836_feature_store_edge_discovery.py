import csv, math
from pathlib import Path
from mind_trader.app.backtest.market_core import ingest_ohlcv_csv
from mind_trader.app.engines.feature_store_edge_discovery import build_features_from_rows, scan_feature_hypotheses, feature_store_report, save_feature_report

def make_rows(n=140):
    rows=[]; p=100
    for i in range(n):
        p += math.sin(i/8)*0.2 + 0.05
        rows.append({"ts":f"2026-01-01T{i//60+9:02d}:{i%60:02d}:00","open":p-0.1,"high":p+0.3,"low":p-0.3,"close":p,"volume":1000+i+(50 if i%20==0 else 0)})
    return rows

def write_csv(path):
    rows=make_rows()
    with open(path,"w",encoding="utf-8",newline="") as f:
        w=csv.writer(f); w.writerow(["ts","open","high","low","close","volume"])
        for r in rows: w.writerow([r["ts"],r["open"],r["high"],r["low"],r["close"],r["volume"]])

def test_build_features_from_rows():
    fs=build_features_from_rows(make_rows(),window=20)
    assert len(fs)>100
    assert "ret_fwd_1" in fs[0]
    assert "regime" in fs[0]

def test_scan_feature_hypotheses_research_only():
    fs=build_features_from_rows(make_rows(),window=20)
    h=scan_feature_hypotheses(fs,min_samples=5)
    assert len(h)>0
    assert h[0]["classification"]=="HYPOTHESIS_ONLY"
    assert h[0]["edge_claim"]=="NONE"
    assert h[0]["production"]=="BLOCKED"

def test_feature_store_report_from_db(tmp_path):
    p=tmp_path/"ohlcv.csv"; dbp=tmp_path/"m.sqlite"; write_csv(p)
    ingest_ohlcv_csv(p,"TEST","1m",str(dbp))
    r=feature_store_report("TEST","1m",str(dbp))
    assert r["feature_rows"]>100
    assert r["decision"]=="RESEARCH_ONLY"
    assert r["production"]=="BLOCKED"

def test_insufficient_rows_returns_empty():
    assert build_features_from_rows(make_rows(10),window=20)==[]

def test_save_feature_report(tmp_path):
    out=save_feature_report({"ok":True},str(tmp_path/"feature.json"))
    assert Path(out).exists()
