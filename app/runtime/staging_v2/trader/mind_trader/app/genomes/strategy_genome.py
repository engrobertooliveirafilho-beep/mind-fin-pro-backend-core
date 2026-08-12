import hashlib, itertools, json
from pathlib import Path

ALLOWED_REGIMES = {
    "TREND_UP",
    "TREND_DOWN",
    "RANGE_SIDEWAYS",
    "COMPRESSION_LOW_VOL",
    "EXPANSION_HIGH_VOL",
    "MIXED_TRANSITION"
}

def stable_hash(obj):
    raw=json.dumps(obj,sort_keys=True,ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def make_genome(strategy_type, symbol, timeframe, regime, params, session="ANY"):
    g={
        "strategy_type":strategy_type,
        "symbol":symbol,
        "timeframe":timeframe,
        "regime":regime,
        "session":session,
        "params":params,
        "production":"BLOCKED",
        "edge_claim":"NONE"
    }
    g["genome_id"]=stable_hash(g)[:24]
    return g

def validate_genome(genome):
    required=["strategy_type","symbol","timeframe","regime","params","genome_id"]
    missing=[k for k in required if k not in genome]
    if missing: return False, f"MISSING:{missing}"
    if genome["regime"] not in ALLOWED_REGIMES:
        return False, "REGIME_NOT_ALLOWED_OR_UNDEFINED"
    if not isinstance(genome["params"],dict) or not genome["params"]:
        return False, "PARAMS_EMPTY"
    return True, "GENOME_OK"

def generate_sma_genomes(symbols=("TEST",), timeframes=("1m",), regimes=("TREND_UP","TREND_DOWN")):
    out=[]
    for symbol,timeframe,regime,fast,slow in itertools.product(symbols,timeframes,regimes,[5,9,12],[21,34,55]):
        if fast<slow:
            out.append(make_genome("SMA_CROSS",symbol,timeframe,regime,{"fast":fast,"slow":slow,"stop_atr":1.5,"target_r":2.0}))
    return out

def generate_breakout_genomes(symbols=("TEST",), timeframes=("1m",), regimes=("COMPRESSION_LOW_VOL","EXPANSION_HIGH_VOL")):
    out=[]
    for symbol,timeframe,regime,lookback,buffer in itertools.product(symbols,timeframes,regimes,[10,20,30],[0.0,0.1,0.2]):
        out.append(make_genome("BREAKOUT",symbol,timeframe,regime,{"lookback":lookback,"buffer":buffer,"stop_atr":1.2,"target_r":2.5}))
    return out

def generate_pullback_genomes(symbols=("TEST",), timeframes=("1m",), regimes=("TREND_UP","TREND_DOWN")):
    out=[]
    for symbol,timeframe,regime,ema,depth in itertools.product(symbols,timeframes,regimes,[20,50],[0.382,0.5,0.618]):
        out.append(make_genome("PULLBACK",symbol,timeframe,regime,{"ema":ema,"pullback_depth":depth,"stop_atr":1.0,"target_r":1.8}))
    return out

def generate_strategy_genomes(symbols=("TEST",), timeframes=("1m",)):
    genomes=[]
    genomes += generate_sma_genomes(symbols,timeframes)
    genomes += generate_breakout_genomes(symbols,timeframes)
    genomes += generate_pullback_genomes(symbols,timeframes)
    unique={g["genome_id"]:g for g in genomes}
    return list(unique.values())

def rank_genomes_by_validation(genomes, validation_reports):
    ranked=[]
    for g in genomes:
        r=validation_reports.get(g["genome_id"],{})
        score=0
        if r.get("classification")=="PAPER_TRADING_CANDIDATE": score+=100
        if r.get("classification")=="RESEARCH_CANDIDATE": score+=40
        m=r.get("out_of_sample",{})
        score += float(m.get("expectancy",0))*10
        score += min(float(m.get("profit_factor",0)),5)*5
        score -= float(m.get("max_drawdown",0))*0.1
        ranked.append({"genome_id":g["genome_id"],"strategy_type":g["strategy_type"],"regime":g["regime"],"score":score,"classification":r.get("classification","UNTESTED_RESEARCH_ONLY"),"production":"BLOCKED"})
    return sorted(ranked,key=lambda x:x["score"],reverse=True)

def save_genomes(genomes,path="mind_trader/reports/P8.32_strategy_genomes.json"):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(genomes,ensure_ascii=False,indent=2),encoding="utf-8")
    return path
