import json, hashlib, itertools, random
from pathlib import Path

FAMILIES=["trend_following","mean_reversion","breakout","pullback","volatility_expansion","liquidity_sweep","range_compression","order_flow","volume_profile","vwap","hybrid","multi_signal"]
SIGNALS=["sma_cross","ema_cross","rsi","macd","atr_break","bollinger","donchian","vwap_distance","volume_zscore","range_compression","liquidity_sweep","gap_reversion"]
RISK_MODELS=["fixed_bps","atr_stop","vol_target","kelly_capped","ftmo_guarded"]
REGIMES=["trend","range","high_vol","low_vol","news_avoidance","session_open","session_close"]

def gid(g):
    return hashlib.sha256(json.dumps(g,sort_keys=True).encode()).hexdigest()[:18]

def generate_genomes(n=10000,seed=92):
    rnd=random.Random(seed); out=[]
    for i in range(n):
        g={
            "family":rnd.choice(FAMILIES),
            "primary_signal":rnd.choice(SIGNALS),
            "secondary_signal":rnd.choice(SIGNALS),
            "risk_model":rnd.choice(RISK_MODELS),
            "regime_filter":rnd.choice(REGIMES),
            "fast":rnd.choice([3,5,8,13,21,34]),
            "slow":rnd.choice([55,89,144,233,377]),
            "threshold":rnd.choice([0.1,0.25,0.5,0.75,1.0,1.5,2.0]),
            "hold_bars":rnd.choice([1,2,3,5,8,13,21,34]),
            "stop_mult":rnd.choice([0.5,0.75,1,1.5,2,3]),
            "target_mult":rnd.choice([0.5,1,1.5,2,3,5]),
            "max_daily_loss_guard":True,
            "live_allowed":False,
            "promotion_allowed":False,
            "index":i
        }
        g["genome_id"]=gid(g); out.append(g)
    return out

def run(n=10000):
    out=Path("reports/P9.2_GENOME_EXPLOSION_ENGINE"); out.mkdir(parents=True,exist_ok=True)
    genomes=generate_genomes(n)
    manifest={
        "STATUS":"P9.2_GENOME_EXPLOSION_ENGINE_IMPLEMENTED",
        "GENOMES":len(genomes),
        "UNIQUE":len({g["genome_id"] for g in genomes}),
        "FAMILIES":FAMILIES,
        "SIGNALS":SIGNALS,
        "RISK_MODELS":RISK_MODELS,
        "REGIMES":REGIMES,
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "EDGE":"NONE",
        "CAUSALITY":"NOT_PROVEN",
        "EXPORT_READY":True
    }
    (out/"P9.2_genomes.json").write_text(json.dumps(genomes,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P9.2_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    return manifest

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
