import csv, math
from pathlib import Path
from mind_trader.app.backtest.market_core import ingest_ohlcv_csv
from mind_trader.app.engines.edge_discovery_authority import edge_discovery_authority, hypothesis_to_validation_report

def write_csv(path):
    price=100
    with open(path,"w",encoding="utf-8",newline="") as f:
        w=csv.writer(f)
        w.writerow(["ts","open","high","low","close","volume"])
        for i in range(180):
            price += math.sin(i/8)*0.2 + 0.03
            w.writerow([f"2026-01-01T{i//60+9:02d}:{i%60:02d}:00",price-0.1,price+0.2,price-0.2,price,1000+i])

def test_hypothesis_to_validation_report():
    h={"hit_rate":0.6,"avg_forward_return":0.002,"sample_size":50}
    r=hypothesis_to_validation_report(h)
    assert r["out_of_sample"]["trades"]==50
    assert r["out_of_sample"]["expectancy"]>0

def test_edge_discovery_authority_runs(tmp_path):
    p=tmp_path/"ohlcv.csv"; dbp=tmp_path/"m.sqlite"; write_csv(p)
    ingest_ohlcv_csv(p,"TEST","1m",str(dbp))
    r=edge_discovery_authority("TEST","1m",str(dbp))
    assert r["decision"]=="EDGE_DISCOVERY_RESEARCH_ONLY"
    assert r["production"]=="BLOCKED"
    assert r["live"]=="FORBIDDEN"
    assert r["edge_claim"]=="NONE"

def test_edge_discovery_report_written(tmp_path):
    p=tmp_path/"ohlcv.csv"; dbp=tmp_path/"m.sqlite"; write_csv(p)
    ingest_ohlcv_csv(p,"TEST","1m",str(dbp))
    edge_discovery_authority("TEST","1m",str(dbp))
    assert Path("mind_trader/reports/P8.79_edge_discovery_authority.json").exists()
