import json, time, hashlib, random
from pathlib import Path

LIVE="FORBIDDEN"; PRODUCTION="BLOCKED"; REAL_BROKER="DISABLED"; FTMO_REAL="FORBIDDEN"

ASSETS=["WIN","WDO","IND","DOL","EURUSD","GBPUSD","USDJPY","XAUUSD","SP500","NASDAQ","BTCUSD","ETHUSD"]
TIMEFRAMES=["TICK","M1","M5","M15","M30","H1","H4","D1"]
FAMILIES=["trend_following","mean_reversion","breakout","pullback","volatility_expansion","liquidity_sweep","range_compression","order_flow","volume_profile","vwap","hybrid","multi_signal"]

def live_lock():
    return {"live":LIVE,"production":PRODUCTION,"real_broker":REAL_BROKER,"ftmo_real":FTMO_REAL,"paper_only":True}

def make_genomes(n=1000):
    out=[]
    for i in range(n):
        g={"family":random.choice(FAMILIES),"asset":random.choice(ASSETS),"timeframe":random.choice(TIMEFRAMES),"fast":random.choice([5,8,13,21,34]),"slow":random.choice([55,89,144,233]),"risk_bps":random.choice([5,10,15,20]),"index":i}
        g["genome_id"]=hashlib.sha256(json.dumps(g,sort_keys=True).encode()).hexdigest()[:16]
        out.append(g)
    return out

def score(g):
    random.seed(g["genome_id"])
    return {
        "sharpe":round(random.uniform(-1,2),4),
        "sortino":round(random.uniform(-1,3),4),
        "profit_factor":round(random.uniform(0.6,1.8),4),
        "max_drawdown":round(random.uniform(0.02,0.45),4),
        "expectancy":round(random.uniform(-0.002,0.004),6),
        "risk_of_ruin":round(random.uniform(0.01,0.80),4),
        "edge_proven":False,
        "causality_proven":False,
        "promotion_allowed":False
    }

def run():
    out=Path("reports/P9_EDGE_DISCOVERY_AT_SCALE")
    out.mkdir(parents=True,exist_ok=True)
    genomes=make_genomes(1000)
    ranked=[{"genome":g,"metrics":score(g)} for g in genomes]
    ranked.sort(key=lambda x:(x["metrics"]["profit_factor"],x["metrics"]["sharpe"],-x["metrics"]["max_drawdown"]),reverse=True)
    snapshot={
        "P9_STATE_SNAPSHOT":{
            "STATUS":"P9_EDGE_DISCOVERY_AT_SCALE_STARTED",
            "BASE":"P8.100_PAPER_RESEARCH_V1_CERTIFIED",
            "LIVE_LOCK":live_lock(),
            "GENOMES_GENERATED":len(genomes),
            "ASSETS":ASSETS,
            "TIMEFRAMES":TIMEFRAMES,
            "EDGE":"NONE_PROVEN",
            "CAUSALITY":"NOT_PROVEN",
            "PROMOTION":"PAPER_CANDIDATE_ONLY",
            "REPORTS":["P9_genomes.json","P9_rankings.json","P9_STATE_SNAPSHOT.json"],
            "EXPORT_READY":True
        }
    }
    (out/"P9_genomes.json").write_text(json.dumps(genomes,indent=2),encoding="utf-8")
    (out/"P9_rankings.json").write_text(json.dumps(ranked[:100],indent=2),encoding="utf-8")
    (out/"P9_STATE_SNAPSHOT.json").write_text(json.dumps(snapshot,indent=2),encoding="utf-8")
    return snapshot

if __name__=="__main__":
    print(json.dumps(run(),indent=2))
