import csv, math
from pathlib import Path
from mind_trader.app.backtest.market_core import ingest_ohlcv_csv, load_ohlcv, backtest_sma_cross, walk_forward, save_report

def make_real_csv(path):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    with open(path,"w",encoding="utf-8",newline="") as f:
        w=csv.writer(f); w.writerow(["ts","open","high","low","close","volume"])
        price=100.0
        for i in range(140):
            price += math.sin(i/7)*0.8 + 0.08
            w.writerow([f"2026-01-01T{i//60+9:02d}:{i%60:02d}:00",price-0.2,price+0.5,price-0.5,price,1000+i])

def test_ingest_and_load_real_csv(tmp_path):
    p=tmp_path/"ohlcv.csv"; make_real_csv(p)
    dbp=tmp_path/"m.sqlite"
    r=ingest_ohlcv_csv(p,"TEST","1m",str(dbp))
    assert r["ingested_rows_seen"]==140
    assert len(load_ohlcv("TEST","1m",str(dbp)))==140

def test_backtest_requires_real_data(tmp_path):
    p=tmp_path/"ohlcv.csv"; make_real_csv(p)
    dbp=tmp_path/"m.sqlite"; ingest_ohlcv_csv(p,"TEST","1m",str(dbp))
    r=backtest_sma_cross("TEST","1m",db_path=str(dbp))
    assert r["edge_claim"]=="NONE"
    assert r["decision"]=="RESEARCH_ONLY_NOT_PROMOTED"
    assert "metrics" in r

def test_walk_forward_not_promotes_to_production(tmp_path):
    p=tmp_path/"ohlcv.csv"; make_real_csv(p)
    dbp=tmp_path/"m.sqlite"; ingest_ohlcv_csv(p,"TEST","1m",str(dbp))
    r=walk_forward("TEST","1m",db_path=str(dbp))
    assert r["decision"] in ["NOT_PROMOTED","CANDIDATE_REQUIRES_MORE_VALIDATION"]

def test_save_report(tmp_path):
    out=save_report({"ok":True},str(tmp_path/"r.json"))
    assert Path(out).exists()

