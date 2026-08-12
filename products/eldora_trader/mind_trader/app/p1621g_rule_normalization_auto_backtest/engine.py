import json, hashlib
from pathlib import Path
from datetime import datetime, UTC

INP=Path("reports/P16.21F_TRANSCRIPT_DOWNLOAD_STRATEGY_EXTRACTION/p1621f_structured_hypotheses.json")
OUT=Path("reports/P16.21G_RULE_NORMALIZATION_AUTO_BACKTEST")
DATA=Path("data")

BLOCKS={"LIVE":"FORBIDDEN","REAL_BROKER":"DISABLED","REAL_ORDERS":"FORBIDDEN","FTMO_REAL":"FORBIDDEN","CAUSALITY":"NOT_PROVEN"}

def load():
    return json.loads(INP.read_text(encoding="utf-8")) if INP.exists() else []

def sig(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:24]

def normalize_rule(h):
    rules=h.get("extracted_rules",[])
    family="GENERIC"
    if "RSI_SIGNAL" in rules: family="RSI"
    if "VWAP_FILTER" in rules: family="VWAP"
    if "MACD_CROSS" in rules: family="MACD"
    if "MOVING_AVERAGE_FILTER" in rules: family="MA"
    if "BREAKOUT" in rules: family="BREAKOUT"
    asset=(h.get("assets") or ["UNRESOLVED"])[0] if isinstance(h.get("assets"),list) and h.get("assets") else "UNRESOLVED"
    tf="H1"
    return {**h,"normalized_strategy_id":sig(h),"normalized_family":family,"normalized_asset":asset,"normalized_timeframe":tf,"status":"HYPOTHESIS_ONLY",**BLOCKS}

def find_dataset(asset,tf):
    if asset=="UNRESOLVED": return None
    files=list(Path(".").glob(f"**/{asset}_{tf}_normalized.csv"))
    return str(files[0]) if files else None

def paper_backtest_stub(s):
    ds=find_dataset(s["normalized_asset"],s["normalized_timeframe"])
    if not ds:
        return {**s,"dataset":None,"backtest_status":"REJECTED_NO_DATASET","edge_status":"NOT_APPROVED",**BLOCKS}
    return {**s,"dataset":ds,"backtest_status":"BACKTEST_PENDING_REAL_ENGINE","edge_status":"NOT_APPROVED",**BLOCKS}

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    normalized=[normalize_rule(x) for x in load()]
    results=[paper_backtest_stub(x) for x in normalized]
    approved=[x for x in results if x.get("edge_status")=="PAPER_RESEARCH_CERTIFIED"]
    report={
        "STATUS":"P16.21G_RULE_NORMALIZATION_AUTO_BACKTEST_IMPLEMENTED",
        "INPUT_STRUCTURED_HYPOTHESES":len(normalized),
        "BACKTEST_QUEUE_ITEMS":len(results),
        "APPROVED_EDGES":len(approved),
        "NEXT":"P16.21H_DATASET_EXPANSION_FOR_VIDEO_STRATEGIES",
        **BLOCKS,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (OUT/"p1621g_normalized_rules.json").write_text(json.dumps(normalized,indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"p1621g_backtest_queue_results.json").write_text(json.dumps(results,indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"p1621g_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    return report

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
