import json, subprocess
from pathlib import Path
from datetime import datetime, UTC

INP=Path("reports/P16.21E_REAL_VIDEO_FETCH_LOOP/p1621e_actionable_video_hypotheses.json")
OUT=Path("reports/P16.21F_TRANSCRIPT_DOWNLOAD_STRATEGY_EXTRACTION")

BLOCKS={"LIVE":"FORBIDDEN","REAL_BROKER":"DISABLED","REAL_ORDERS":"FORBIDDEN","FTMO_REAL":"FORBIDDEN","CAUSALITY":"NOT_PROVEN"}

def load():
    return json.loads(INP.read_text(encoding="utf-8")) if INP.exists() else []

def fetch_subtitles(video_url):
    if not video_url:
        return {"status":"NO_URL","text":""}
    try:
        p=subprocess.run(["yt-dlp","--skip-download","--write-auto-subs","--sub-langs","pt,en","--sub-format","vtt","--print","title",video_url],capture_output=True,text=True,timeout=120)
        return {"status":"FETCH_ATTEMPTED","text":((p.stdout or "")+"\n"+(p.stderr or ""))[:5000]}
    except Exception as e:
        return {"status":"FETCH_ERROR","text":str(e)}

def extract_rules(text, meta):
    t=(text or "").lower()+" "+json.dumps(meta,ensure_ascii=False).lower()
    rules=[]
    if "rsi" in t: rules.append("RSI_SIGNAL")
    if "vwap" in t: rules.append("VWAP_FILTER")
    if "macd" in t: rules.append("MACD_CROSS")
    if "média" in t or "media" in t or "ema" in t: rules.append("MOVING_AVERAGE_FILTER")
    if "rompimento" in t or "breakout" in t: rules.append("BREAKOUT")
    if "pullback" in t: rules.append("PULLBACK")
    if "stop" in t: rules.append("STOP_REQUIRED")
    if "alvo" in t or "target" in t: rules.append("TARGET_REQUIRED")
    return sorted(set(rules)) or ["UNSTRUCTURED_STRATEGY_TEXT"]

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    rows=[]
    for item in load():
        sub=fetch_subtitles(item.get("url"))
        rules=extract_rules(sub.get("text",""),item)
        rows.append({**item,"transcript_fetch_status":sub["status"],"transcript_sample":sub["text"][:1000],"extracted_rules":rules,"status":"HYPOTHESIS_ONLY","backtest_status":"PENDING_RULE_NORMALIZATION",**BLOCKS})
    structured=[x for x in rows if x["extracted_rules"]!=["UNSTRUCTURED_STRATEGY_TEXT"]]
    report={"STATUS":"P16.21F_TRANSCRIPT_DOWNLOAD_STRATEGY_EXTRACTION_IMPLEMENTED","INPUT_VIDEOS":len(rows),"STRUCTURED_STRATEGY_HYPOTHESES":len(structured),"UNSTRUCTURED":len(rows)-len(structured),"NEXT":"P16.21G_RULE_NORMALIZATION_AND_AUTO_BACKTEST",**BLOCKS,"generated_at":datetime.now(UTC).isoformat()}
    (OUT/"p1621f_transcript_strategy_hypotheses.json").write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"p1621f_structured_hypotheses.json").write_text(json.dumps(structured,indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"p1621f_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    return report

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
