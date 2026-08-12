import csv, math
from pathlib import Path
from mind_trader.app.backtest.market_core import ingest_ohlcv_csv
from mind_trader.app.genomes.strategy_genome import generate_strategy_genomes, make_genome
from mind_trader.app.backtest.massive_cluster import run_genome_backtest, massive_backtest_cluster, save_cluster_report

def write_csv(path):
    p=100
    with open(path,"w",encoding="utf-8",newline="") as f:
        w=csv.writer(f); w.writerow(["ts","open","high","low","close","volume"])
        for i in range(180):
            p += math.sin(i/8)*0.3 + 0.05
            w.writerow([f"2026-01-01T{i//60+9:02d}:{i%60:02d}:00",p-0.1,p+0.3,p-0.3,p,1000+i])

def seed(tmp_path):
    p=tmp_path/"ohlcv.csv"; dbp=tmp_path/"m.sqlite"; write_csv(p); ingest_ohlcv_csv(p,"TEST","1m",str(dbp)); return dbp

def test_run_valid_sma_genome(tmp_path):
    dbp=seed(tmp_path)
    g=make_genome("SMA_CROSS","TEST","1m","TREND_UP",{"fast":5,"slow":21})
    r=run_genome_backtest(g,str(dbp))
    assert r["status"] in ["TESTED","FAILED"]
    assert r["production"]=="BLOCKED"
    assert r["edge_claim"]=="NONE"

def test_blocks_invalid_genome(tmp_path):
    dbp=seed(tmp_path)
    g=make_genome("SMA_CROSS","TEST","1m","UNDEFINED",{"fast":5,"slow":21})
    r=run_genome_backtest(g,str(dbp))
    assert r["status"]=="BLOCKED"

def test_cluster_runs_and_stays_research_only(tmp_path):
    dbp=seed(tmp_path)
    gs=generate_strategy_genomes(symbols=("TEST",),timeframes=("1m",))
    r=massive_backtest_cluster(gs,str(dbp),limit=10)
    assert r["executed"]==10
    assert r["decision"]=="RESEARCH_ONLY"
    assert r["production"]=="BLOCKED"
    assert r["edge_claim"]=="NONE"

def test_breakout_strategy_now_supported(tmp_path):
    dbp=seed(tmp_path)
    g=make_genome("BREAKOUT","TEST","1m","EXPANSION_HIGH_VOL",{"lookback":20,"buffer":0.0})
    r=run_genome_backtest(g,str(dbp))
    assert r["status"]=="TESTED"

def test_save_cluster_report(tmp_path):
    out=save_cluster_report({"ok":True},str(tmp_path/"cluster.json"))
    assert Path(out).exists()
