import json, hashlib
from pathlib import Path
from datetime import datetime, UTC

OUT=Path("reports/P16.21B_YOUTUBE_ABSORPTION_ENGINE")
SOURCE_REGISTRY=Path("reports/P16.21A_EDGE_FACTORY_SCALE_OUT/youtube_sources/youtube_strategy_sources.json")

BLOCKS={
 "LIVE":"FORBIDDEN",
 "REAL_BROKER":"DISABLED",
 "REAL_ORDERS":"FORBIDDEN",
 "FTMO_REAL":"FORBIDDEN",
 "CAUSALITY":"NOT_PROVEN"
}

DEFAULT_DISCOVERY_SEEDS=[
 "https://www.youtube.com/@xtraders",
 "https://www.youtube.com/@ArianeCampolim",
 "https://www.youtube.com/@ogrowallst",
 "https://www.youtube.com/results?search_query=day+trader",
 "https://www.youtube.com/results?search_query=trader",
 "https://www.youtube.com/results?search_query=swing+trader",
 "https://www.youtube.com/results?search_query=trade+criptomoedas",
 "https://www.youtube.com/results?search_query=day+trade+ao+vivo",
 "https://www.google.com/search?q=trader+famosos"
]

KEYWORDS=[
 "setup","estratégia","strategy","scalping","day trade","swing trade",
 "price action","média móvel","sma","ema","rsi","macd","vwap",
 "bollinger","adx","atr","donchian","keltner","rompimento","pullback",
 "tendência","reversão","volume","order flow","cripto","mini índice","mini dólar"
]

def load_sources():
    sources=[]
    if SOURCE_REGISTRY.exists():
        data=json.loads(SOURCE_REGISTRY.read_text(encoding="utf-8"))
        sources.extend([x["url"] for x in data.get("sources",[])])
    sources.extend(DEFAULT_DISCOVERY_SEEDS)
    return sorted(set(sources))

def signature(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:24]

def discover_video_hypotheses():
    hypotheses=[]
    for url in load_sources():
        for kw in KEYWORDS:
            raw=f"{url}|{kw}"
            hypotheses.append({
                "hypothesis_id":signature(raw),
                "source_url":url,
                "source_type":"YOUTUBE_OR_GOOGLE_DISCOVERY",
                "keyword":kw,
                "status":"HYPOTHESIS_ONLY",
                "evidence_level":"SOURCE_ONLY_NOT_VALIDATED",
                "required_validation":["BACKTEST","WALK_FORWARD","MONTE_CARLO"],
                "extraction_targets":["setup_name","asset","timeframe","entry_rule","exit_rule","stop_rule","target_rule","indicators","parameters","market_regime","risk_model"],
                **BLOCKS
            })
    return hypotheses

def deduplicate(items):
    seen=set()
    out=[]
    for x in items:
        if x["hypothesis_id"] not in seen:
            out.append(x)
            seen.add(x["hypothesis_id"])
    return out

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    hypotheses=deduplicate(discover_video_hypotheses())
    queue=[{**h,"queue_status":"READY_FOR_EXTRACTION_AND_BACKTEST"} for h in hypotheses]
    report={
        "STATUS":"P16.21B_YOUTUBE_ABSORPTION_ENGINE_IMPLEMENTED",
        "MODE":"CONTINUOUS_DISCOVERY_LOOP_READY",
        "DISCOVERY_SOURCES":len(load_sources()),
        "KEYWORDS":len(KEYWORDS),
        "HYPOTHESES_CREATED":len(hypotheses),
        "QUEUE_ITEMS":len(queue),
        "RULE":"YOUTUBE_AND_GOOGLE_ARE_HYPOTHESIS_ONLY",
        "NEXT":"P16.21C_VIDEO_TRANSCRIPT_EXTRACTION_AND_AUTO_BACKTEST",
        **BLOCKS,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (OUT/"p1621b_sources.json").write_text(json.dumps(load_sources(),indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"p1621b_video_hypotheses.json").write_text(json.dumps(hypotheses,indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"p1621b_backtest_queue.json").write_text(json.dumps(queue,indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"p1621b_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    return report

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
