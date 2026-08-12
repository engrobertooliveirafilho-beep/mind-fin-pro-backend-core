import json, random
from pathlib import Path
from datetime import datetime, UTC
from mind_trader.app.backtest.market_core import load_ohlcv
from mind_trader.app.engines.causality_hypothesis import multi_lag_scan, causality_hypothesis_from_scan
from mind_trader.app.engines.cross_asset_brain import align_returns, corr

def placebo_lag_test(rows_a, rows_b, max_lag=5, runs=50, seed=826):
    xs,ys,ts=align_returns(rows_a,rows_b)
    if len(xs)<max_lag+20:
        return {"passed":False,"reason":"INSUFFICIENT_DATA","runs":runs}
    rnd=random.Random(seed)
    real=max(abs(x["a_leads_edge_over_base"]) for x in multi_lag_scan(rows_a,rows_b,max_lag))
    placebo=[]
    for _ in range(runs):
        shuffled=ys[:]
        rnd.shuffle(shuffled)
        base=corr(xs,shuffled)
        best=0
        for lag in range(1,max_lag+1):
            best=max(best,abs(corr(xs[:-lag],shuffled[lag:])-base))
        placebo.append(best)
    threshold=sorted(placebo)[int(0.95*(len(placebo)-1))]
    return {"passed":real>threshold,"real_score":real,"placebo_p95":threshold,"runs":runs}

def causality_authority(asset_a, asset_b, timeframe, db_path="mind_trader/data/market.sqlite", max_lag=5):
    a=load_ohlcv(asset_a,timeframe,db_path)
    b=load_ohlcv(asset_b,timeframe,db_path)
    scan=multi_lag_scan(a,b,max_lag)
    hyp=causality_hypothesis_from_scan(asset_a,asset_b,scan)
    placebo=placebo_lag_test(a,b,max_lag)
    decision="CAUSAL_RESEARCH_HYPOTHESIS" if hyp["decision"]=="RESEARCH_ONLY_CAUSAL_HYPOTHESIS" and placebo["passed"] else "REJECT_OR_RETEST_CAUSAL_HYPOTHESIS"
    report={
        "authority":"P8.77_CAUSALITY_AUTHORITY",
        "created_at":datetime.now(UTC).isoformat(),
        "asset_a":asset_a,
        "asset_b":asset_b,
        "timeframe":timeframe,
        "hypothesis":hyp,
        "placebo":placebo,
        "decision":decision,
        "causality_claim":"NOT_PROVEN",
        "edge_claim":"NONE",
        "production":"BLOCKED",
        "live":"FORBIDDEN"
    }
    Path("mind_trader/reports").mkdir(parents=True,exist_ok=True)
    Path("mind_trader/reports/P8.77_causality_authority.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    return report

def veto_if_causality_not_proven(report):
    return {
        "allowed":False,
        "decision":"VETO_CAUSALITY_NOT_PROVEN",
        "source_decision":report.get("decision"),
        "causality_claim":report.get("causality_claim","NOT_PROVEN"),
        "production":"BLOCKED",
        "edge_claim":"NONE"
    }
