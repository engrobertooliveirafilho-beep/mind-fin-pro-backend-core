import csv
from pathlib import Path
from app.p146_strategy_promotion_engine.engine import score, run, SOURCE_DIR

def test_p146_score_promotes_good_result():
    r=score({"strategy_id":"s1","asset":"WIN","timeframe":"M1","profit_factor":"1.8","drawdown":"1000","winrate":"57","trades":"300"})
    assert r["paper_promoted"] is True
    assert r["real_orders"]=="FORBIDDEN"

def test_p146_score_rejects_bad_result():
    r=score({"strategy_id":"s2","asset":"WIN","timeframe":"M1","profit_factor":"0.9","drawdown":"9000","winrate":"40","trades":"20"})
    assert r["paper_promoted"] is False

def test_p146_run_with_sample_file():
    SOURCE_DIR.mkdir(parents=True,exist_ok=True)
    p=SOURCE_DIR/"sample_backtest.csv"
    with open(p,"w",newline="",encoding="utf-8") as f:
        w=csv.writer(f)
        w.writerow(["strategy_id","asset","timeframe","profit_factor","drawdown","winrate","trades"])
        w.writerow(["s1","WIN","M1","1.8","1000","57","300"])
    m=run()
    assert m["STATUS"]=="P14.6_STRATEGY_PROMOTION_ENGINE_IMPLEMENTED"
    assert m["REAL_ORDERS"]=="FORBIDDEN"
    assert m["EXPORT_READY"] is True
