import csv, math
from pathlib import Path
from mind_trader.app.backtest.market_core import ingest_ohlcv_csv
from mind_trader.app.genomes.strategy_genome import make_genome, generate_strategy_genomes
from mind_trader.app.backtest.massive_cluster import run_genome_backtest, massive_backtest_cluster, backtest_breakout, backtest_pullback

def seed(tmp_path):
    p=tmp_path/"ohlcv.csv"; dbp=tmp_path/"m.sqlite"; price=100
    with open(p,"w",encoding="utf-8",newline="") as f:
        w=csv.writer(f); w.writerow(["ts","open","high","low","close","volume"])
        for i in range(220):
            price += math.sin(i/8)*0.3 + 0.05
            w.writerow([f"2026-01-01T{i//60+9:02d}:{i%60:02d}:00",price-0.1,price+0.3,price-0.3,price,1000+i])
    ingest_ohlcv_csv(p,"TEST","1m",str(dbp)); return dbp

def test_breakout_real_engine_runs(tmp_path):
    dbp=seed(tmp_path)
    r=backtest_breakout("TEST","1m",db_path=str(dbp))
    assert r["strategy"]=="BREAKOUT"
    assert r["production"]=="BLOCKED"

def test_pullback_real_engine_runs(tmp_path):
    dbp=seed(tmp_path)
    r=backtest_pullback("TEST","1m",db_path=str(dbp))
    assert r["strategy"]=="PULLBACK"
    assert r["edge_claim"]=="NONE"

def test_breakout_genome_is_tested_not_skipped(tmp_path):
    dbp=seed(tmp_path)
    g=make_genome("BREAKOUT","TEST","1m","EXPANSION_HIGH_VOL",{"lookback":20,"buffer":0.0})
    r=run_genome_backtest(g,str(dbp))
    assert r["status"]=="TESTED"

def test_pullback_genome_is_tested_not_skipped(tmp_path):
    dbp=seed(tmp_path)
    g=make_genome("PULLBACK","TEST","1m","TREND_UP",{"ema":20,"pullback_depth":0.5})
    r=run_genome_backtest(g,str(dbp))
    assert r["status"]=="TESTED"

def test_cluster_tests_multiple_strategy_families(tmp_path):
    dbp=seed(tmp_path)
    gs=generate_strategy_genomes(symbols=("TEST",),timeframes=("1m",))
    r=massive_backtest_cluster(gs,str(dbp),limit=999)
    tested={x.get("backtest",{}).get("strategy") for x in r["ranking"] if x["status"]=="TESTED"}
    assert "SMA_CROSS" in tested
    assert "BREAKOUT" in tested
    assert "PULLBACK" in tested
    assert r["production"]=="BLOCKED"


