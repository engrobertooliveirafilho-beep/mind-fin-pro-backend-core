import json
from pathlib import Path
from mind_trader.app.backtest.market_core import load_ohlcv
from mind_trader.app.engines.cross_asset_brain import align_returns, corr

def multi_lag_scan(rows_a, rows_b, max_lag=5):
    xs,ys,ts=align_returns(rows_a,rows_b)
    out=[]
    if len(xs)<max_lag+10:
        return out
    base=corr(xs,ys)
    for lag in range(1,max_lag+1):
        ab=corr(xs[:-lag],ys[lag:])
        ba=corr(ys[:-lag],xs[lag:])
        out.append({
            "lag":lag,
            "base_correlation":base,
            "a_leads_b_corr":ab,
            "b_leads_a_corr":ba,
            "a_leads_edge_over_base":ab-base,
            "b_leads_edge_over_base":ba-base,
            "sample_size":len(xs)-lag
        })
    return out

def causality_hypothesis_from_scan(asset_a, asset_b, scan):
    if not scan:
        return {
            "asset_a":asset_a,
            "asset_b":asset_b,
            "hypothesis_strength":"INSUFFICIENT_DATA",
            "direction":"NONE",
            "causality_claim":"NOT_PROVEN",
            "edge_claim":"NONE",
            "production":"BLOCKED"
        }
    best_a=max(scan,key=lambda x:x["a_leads_edge_over_base"])
    best_b=max(scan,key=lambda x:x["b_leads_edge_over_base"])
    a_score=best_a["a_leads_edge_over_base"]
    b_score=best_b["b_leads_edge_over_base"]

    if a_score > b_score and a_score > 0.15:
        direction=f"{asset_a}_MAY_LEAD_{asset_b}"
        score=a_score
    elif b_score > a_score and b_score > 0.15:
        direction=f"{asset_b}_MAY_LEAD_{asset_a}"
        score=b_score
    else:
        direction="NONE"
        score=max(a_score,b_score)

    if score > 0.30:
        strength="STRONG_RESEARCH_HYPOTHESIS"
    elif score > 0.15:
        strength="WEAK_RESEARCH_HYPOTHESIS"
    else:
        strength="NO_CAUSAL_HYPOTHESIS"

    return {
        "asset_a":asset_a,
        "asset_b":asset_b,
        "hypothesis_strength":strength,
        "direction":direction,
        "score":score,
        "best_a_leads_b":best_a,
        "best_b_leads_a":best_b,
        "causality_claim":"NOT_PROVEN",
        "correlation_is_not_causation":True,
        "edge_claim":"NONE",
        "decision":"RESEARCH_ONLY_CAUSAL_HYPOTHESIS" if direction!="NONE" else "REJECT_CAUSAL_HYPOTHESIS",
        "production":"BLOCKED"
    }

def causal_report(asset_a, asset_b, timeframe, db_path="mind_trader/data/market.sqlite", max_lag=5):
    a=load_ohlcv(asset_a,timeframe,db_path)
    b=load_ohlcv(asset_b,timeframe,db_path)
    scan=multi_lag_scan(a,b,max_lag)
    hyp=causality_hypothesis_from_scan(asset_a,asset_b,scan)
    hyp["scan"]=scan
    hyp["timeframe"]=timeframe
    return hyp

def veto_edge_if_causality_unproven(edge_report, causal_hypothesis):
    if causal_hypothesis.get("causality_claim")!="PROVEN":
        return {
            "allowed":False,
            "decision":"VETO_EDGE_CAUSALITY_NOT_PROVEN",
            "edge_report":edge_report,
            "causal_hypothesis":causal_hypothesis,
            "production":"BLOCKED"
        }
    return {"allowed":True,"decision":"CAUSALITY_ACCEPTED_FOR_RESEARCH_ONLY","production":"BLOCKED"}

def save_causal_report(report,path="mind_trader/reports/P8.35_causality_report.json"):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    return path
