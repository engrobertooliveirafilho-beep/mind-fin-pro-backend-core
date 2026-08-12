import json, hashlib
from pathlib import Path
from datetime import datetime, UTC

INQ=Path("reports/P16.21B_YOUTUBE_ABSORPTION_ENGINE/p1621b_backtest_queue.json")
OUT=Path("reports/P16.21C_VIDEO_TRANSCRIPT_EXTRACTION_AUTO_BACKTEST")

BLOCKS={"LIVE":"FORBIDDEN","REAL_BROKER":"DISABLED","REAL_ORDERS":"FORBIDDEN","FTMO_REAL":"FORBIDDEN","CAUSALITY":"NOT_PROVEN"}

def sig(x): return hashlib.sha256(json.dumps(x,sort_keys=True).encode()).hexdigest()[:24]
def loadq(): return json.loads(INQ.read_text(encoding="utf-8")) if INQ.exists() else []

def extract_strategy(h):
    kw=h.get("keyword","").lower()
    fam="SMA"
    if "ema" in kw or "média" in kw: fam="EMA"
    if "rsi" in kw: fam="RSI"
    if "macd" in kw: fam="MACD"
    if "vwap" in kw: fam="VWAP"
    if "bollinger" in kw: fam="BOLLINGER"
    if "adx" in kw: fam="ADX"
    if "atr" in kw: fam="ATR"
    if "donchian" in kw: fam="DONCHIAN"
    return {
        "strategy_id":sig(h),
        "source_hypothesis_id":h["hypothesis_id"],
        "source_url":h["source_url"],
        "family":fam,
        "asset":"UNRESOLVED",
        "timeframe":"UNRESOLVED",
        "status":"HYPOTHESIS_ONLY",
        "extraction_status":"TRANSCRIPT_PENDING",
        "backtest_status":"PENDING_DATASET_MATCH",
        "validation_required":["BACKTEST","WALK_FORWARD","MONTE_CARLO"],
        **BLOCKS
    }

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    queue=loadq()
    strategies=[extract_strategy(x) for x in queue]
    uniq={s["strategy_id"]:s for s in strategies}
    strategies=list(uniq.values())
    report={
        "STATUS":"P16.21C_VIDEO_TRANSCRIPT_EXTRACTION_AUTO_BACKTEST_IMPLEMENTED",
        "INPUT_QUEUE":len(queue),
        "STRATEGIES_EXTRACTED":len(strategies),
        "TRANSCRIPT_MODE":"PENDING_EXTERNAL_FETCHER",
        "BACKTEST_MODE":"PENDING_DATASET_MATCH",
        "RULE":"NO_WEB_VIDEO_STRATEGY_PROMOTION_WITHOUT_BACKTEST_WALK_FORWARD_MONTE_CARLO",
        "NEXT":"P16.21D_REAL_TRANSCRIPT_FETCHER_AND_DATASET_MATCHER",
        **BLOCKS,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (OUT/"p1621c_extracted_strategies.json").write_text(json.dumps(strategies,indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"p1621c_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    return report

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
