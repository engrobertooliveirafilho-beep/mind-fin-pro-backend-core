import json, statistics
from pathlib import Path
from datetime import datetime, UTC
from mind_trader.app.backtest.market_core import load_ohlcv
from mind_trader.app.engines.cross_asset_brain import align_returns, corr, rolling_correlation
from mind_trader.app.engines.regime_detection import detect_regime_from_rows

def confidence_from_sample(n):
    if n >= 500: return "HIGH"
    if n >= 120: return "MEDIUM"
    if n >= 30: return "LOW"
    return "INSUFFICIENT"

def classify_relation(correlation):
    if correlation >= 0.70: return "STRONG_POSITIVE"
    if correlation >= 0.35: return "MODERATE_POSITIVE"
    if correlation <= -0.70: return "STRONG_NEGATIVE"
    if correlation <= -0.35: return "MODERATE_NEGATIVE"
    return "WEAK_OR_NONE"

def correlation_authority_pair(asset_a, asset_b, timeframe, db_path="mind_trader/data/market.sqlite", window=30):
    a=load_ohlcv(asset_a,timeframe,db_path)
    b=load_ohlcv(asset_b,timeframe,db_path)
    xs,ys,ts=align_returns(a,b)

    if len(xs)<window:
        return {
            "asset_a":asset_a,
            "asset_b":asset_b,
            "decision":"INSUFFICIENT_DATA",
            "sample_size":len(xs),
            "production":"BLOCKED",
            "edge_claim":"NONE",
            "causality_claim":"NOT_PROVEN"
        }

    base=corr(xs,ys)
    roll=rolling_correlation(a,b,window)
    regime=detect_regime_from_rows(a,window).get("regime","UNDEFINED")
    last_roll=roll[-1]["correlation"] if roll else base
    divergence=abs(base-last_roll)

    return {
        "asset_a":asset_a,
        "asset_b":asset_b,
        "timeframe":timeframe,
        "sample_size":len(xs),
        "confidence":confidence_from_sample(len(xs)),
        "correlation":base,
        "rolling_last":last_roll,
        "relation":classify_relation(base),
        "regime":regime,
        "divergence":divergence,
        "divergence_flag":divergence>0.35,
        "decision":"CORRELATION_RESEARCH_ONLY",
        "production":"BLOCKED",
        "edge_claim":"NONE",
        "causality_claim":"NOT_PROVEN"
    }

def correlation_matrix_authority(symbols, timeframe, db_path="mind_trader/data/market.sqlite", window=30):
    pairs=[]
    for i,a in enumerate(symbols):
        for b in symbols[i+1:]:
            pairs.append(correlation_authority_pair(a,b,timeframe,db_path,window))
    report={
        "authority":"P8.76_CORRELATION_AUTHORITY",
        "created_at":datetime.now(UTC).isoformat(),
        "symbols":list(symbols),
        "timeframe":timeframe,
        "pairs":pairs,
        "decision":"CORRELATION_MATRIX_RESEARCH_ONLY",
        "production":"BLOCKED",
        "edge_claim":"NONE",
        "causality_claim":"NOT_PROVEN"
    }
    Path("mind_trader/reports").mkdir(parents=True,exist_ok=True)
    Path("mind_trader/reports/P8.76_correlation_authority.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    return report
