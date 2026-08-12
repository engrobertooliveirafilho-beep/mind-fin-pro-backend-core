import json, statistics, math
from pathlib import Path
from mind_trader.app.backtest.market_core import load_ohlcv
from mind_trader.app.engines.regime_detection import detect_regime_from_rows

def safe_mean(x): return statistics.mean(x) if x else 0.0
def safe_stdev(x): return statistics.stdev(x) if len(x)>1 else 0.0

def build_features_from_rows(rows, window=20):
    if len(rows) < window + 2:
        return []
    out=[]
    closes=[float(r["close"]) for r in rows]
    vols=[float(r["volume"]) for r in rows]
    for i in range(window, len(rows)-1):
        c=closes[i]; prev=closes[i-1]
        hist=closes[i-window:i]
        vh=vols[i-window:i]
        ret_1=(c-prev)/prev if prev else 0
        ret_fwd_1=(closes[i+1]-c)/c if c else 0
        vol=safe_stdev([(hist[j]-hist[j-1])/hist[j-1] for j in range(1,len(hist)) if hist[j-1]])
        rng=(float(rows[i]["high"])-float(rows[i]["low"]))/c if c else 0
        mom=(c-hist[0])/hist[0] if hist[0] else 0
        vstd=safe_stdev(vh)
        vz=(vols[i]-safe_mean(vh))/vstd if vstd else 0
        regime=detect_regime_from_rows(rows[:i+1], min(30, i+1)).get("regime","UNDEFINED")
        out.append({
            "ts":rows[i]["ts"],
            "ret_1":ret_1,
            "ret_fwd_1":ret_fwd_1,
            "volatility":vol,
            "range_pct":rng,
            "momentum":mom,
            "volume_zscore":vz,
            "regime":regime
        })
    return out

def bucket_feature(v):
    if v > 0.01: return "HIGH_POS"
    if v > 0.002: return "POS"
    if v < -0.01: return "HIGH_NEG"
    if v < -0.002: return "NEG"
    return "NEUTRAL"

def scan_feature_hypotheses(features, min_samples=10):
    candidates=[]
    keys=["ret_1","volatility","range_pct","momentum","volume_zscore"]
    for k in keys:
        groups={}
        for f in features:
            b=bucket_feature(float(f[k]))
            groups.setdefault((k,b,f["regime"]),[]).append(float(f["ret_fwd_1"]))
        for (feature,bucket,regime),vals in groups.items():
            if len(vals) >= min_samples:
                avg=safe_mean(vals)
                hit=sum(1 for x in vals if x>0)/len(vals)
                score=avg*10000 + (hit-0.5)*10
                candidates.append({
                    "feature":feature,
                    "bucket":bucket,
                    "regime":regime,
                    "sample_size":len(vals),
                    "avg_forward_return":avg,
                    "hit_rate":hit,
                    "score":score,
                    "classification":"HYPOTHESIS_ONLY",
                    "edge_claim":"NONE",
                    "production":"BLOCKED"
                })
    return sorted(candidates,key=lambda x:x["score"],reverse=True)

def feature_store_report(symbol,timeframe,db_path="mind_trader/data/market.sqlite",window=20):
    rows=load_ohlcv(symbol,timeframe,db_path)
    features=build_features_from_rows(rows,window)
    hypotheses=scan_feature_hypotheses(features)
    return {
        "symbol":symbol,
        "timeframe":timeframe,
        "feature_rows":len(features),
        "hypotheses":hypotheses,
        "decision":"RESEARCH_ONLY",
        "edge_claim":"NONE",
        "production":"BLOCKED"
    }

def save_feature_report(report,path="mind_trader/reports/P8.36_feature_store_edge_discovery.json"):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    return path
