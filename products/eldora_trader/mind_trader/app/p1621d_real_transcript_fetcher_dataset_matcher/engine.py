import json, re, hashlib, shutil, subprocess
from pathlib import Path
from datetime import datetime, UTC

INP=Path("reports/P16.21C_VIDEO_TRANSCRIPT_EXTRACTION_AUTO_BACKTEST/p1621c_extracted_strategies.json")
OUT=Path("reports/P16.21D_REAL_TRANSCRIPT_FETCHER_DATASET_MATCHER")

BLOCKS={"LIVE":"FORBIDDEN","REAL_BROKER":"DISABLED","REAL_ORDERS":"FORBIDDEN","FTMO_REAL":"FORBIDDEN","CAUSALITY":"NOT_PROVEN"}

ASSET_PATTERNS={
 "WINFUT":["win","mini índice","mini indice","índice","indice"],
 "WDOFUT":["wdo","mini dólar","mini dolar","dólar","dolar"],
 "IBOV":["ibov","ibovespa"],
 "PETR4":["petr4","petrobras"],
 "VALE3":["vale3","vale"],
 "IFIX":["ifix"],
 "CSAN3":["csan3","cosan"],
 "BTC":["bitcoin","btc","cripto","criptomoedas"]
}

TIMEFRAME_PATTERNS={
 "M15":["15m","m15","15 minutos"],
 "M5":["5m","m5","5 minutos"],
 "M30":["30m","m30","30 minutos"],
 "H1":["h1","1h","60 minutos"],
 "H4":["h4","4h"],
 "D1":["diário","diario","d1","daily"]
}

def load():
    return json.loads(INP.read_text(encoding="utf-8")) if INP.exists() else []

def has_ytdlp():
    return shutil.which("yt-dlp") is not None

def classify_asset(text):
    t=text.lower()
    for asset, keys in ASSET_PATTERNS.items():
        if any(k in t for k in keys):
            return asset
    return "UNRESOLVED"

def classify_timeframe(text):
    t=text.lower()
    for tf, keys in TIMEFRAME_PATTERNS.items():
        if any(k in t for k in keys):
            return tf
    return "UNRESOLVED"

def dataset_match(asset,timeframe):
    if asset=="UNRESOLVED" or timeframe=="UNRESOLVED":
        return None
    candidates=list(Path(".").glob(f"**/{asset}_{timeframe}_normalized.csv"))
    return str(candidates[0]) if candidates else None

def enrich_strategy(s):
    text=" ".join([str(s.get("source_url","")),str(s.get("family","")),str(s.get("asset","")),str(s.get("timeframe",""))])
    asset=classify_asset(text)
    tf=classify_timeframe(text)
    ds=dataset_match(asset,tf)
    return {
        **s,
        "metadata_fetcher":"yt-dlp" if has_ytdlp() else "YT_DLP_NOT_INSTALLED",
        "transcript_status":"PENDING_REAL_FETCH",
        "asset":asset,
        "timeframe":tf,
        "dataset_match":ds,
        "dataset_match_status":"MATCHED" if ds else "UNMATCHED",
        "backtest_status":"READY_FOR_BACKTEST" if ds else "PENDING_DATASET_MATCH",
        **BLOCKS
    }

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    items=[enrich_strategy(x) for x in load()]
    matched=[x for x in items if x["dataset_match_status"]=="MATCHED"]
    report={
        "STATUS":"P16.21D_REAL_TRANSCRIPT_FETCHER_AND_DATASET_MATCHER_IMPLEMENTED",
        "INPUT_STRATEGIES":len(items),
        "YTDLP_AVAILABLE":has_ytdlp(),
        "DATASET_MATCHED":len(matched),
        "DATASET_UNMATCHED":len(items)-len(matched),
        "NEXT":"P16.21E_REAL_VIDEO_FETCH_LOOP_AND_BACKTEST_DISPATCH",
        **BLOCKS,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (OUT/"p1621d_enriched_strategies.json").write_text(json.dumps(items,indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"p1621d_ready_for_backtest.json").write_text(json.dumps(matched,indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"p1621d_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    return report

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))

