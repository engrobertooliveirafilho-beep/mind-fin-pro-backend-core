import json, subprocess, re
from pathlib import Path
from datetime import datetime, UTC

OUT=Path("reports/P16.21E_REAL_VIDEO_FETCH_LOOP")
SOURCES=Path("reports/P16.21B_YOUTUBE_ABSORPTION_ENGINE/p1621b_sources.json")

BLOCKS={"LIVE":"FORBIDDEN","REAL_BROKER":"DISABLED","REAL_ORDERS":"FORBIDDEN","FTMO_REAL":"FORBIDDEN","CAUSALITY":"NOT_PROVEN"}

def load_sources():
    return json.loads(SOURCES.read_text(encoding="utf-8")) if SOURCES.exists() else []

def fetch_metadata(url, limit=5):
    cmd=["yt-dlp","--flat-playlist","--dump-json",f"--playlist-end={limit}",url]
    p=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
    rows=[]
    for line in p.stdout.splitlines():
        try:
            j=json.loads(line)
            rows.append({
                "id":j.get("id"),
                "title":j.get("title"),
                "url":j.get("webpage_url") or j.get("url"),
                "channel":j.get("channel") or j.get("uploader"),
                "source_url":url
            })
        except Exception:
            pass
    return rows

def classify_text(text):
    t=(text or "").lower()
    assets=[]
    if re.search(r"\bwin\b|mini[ -]?índice|mini[ -]?indice|índice|indice",t): assets.append("WINFUT")
    if re.search(r"\bwdo\b|mini[ -]?dólar|mini[ -]?dolar|dólar|dolar",t): assets.append("WDOFUT")
    if "ifix" in t: assets.append("IFIX")
    if "petr4" in t or "petrobras" in t: assets.append("PETR4")
    if "vale3" in t or "vale " in t: assets.append("VALE3")
    if "bitcoin" in t or "btc" in t or "cripto" in t: assets.append("BTC")
    families=[]
    for k in ["sma","ema","rsi","macd","vwap","bollinger","adx","atr","donchian","keltner","price action","order flow"]:
        if k in t: families.append(k.upper())
    return {"assets":sorted(set(assets)),"families":sorted(set(families))}

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    all_rows=[]
    errors=[]
    for src in load_sources():
        try:
            rows=fetch_metadata(src,5)
            for r in rows:
                cls=classify_text(" ".join([str(r.get("title")),str(r.get("channel"))]))
                all_rows.append({**r,**cls,"status":"VIDEO_METADATA_ONLY","hypothesis_status":"HYPOTHESIS_ONLY",**BLOCKS})
        except Exception as e:
            errors.append({"source":src,"error":str(e)})
    actionable=[x for x in all_rows if x["assets"] or x["families"]]
    report={
        "STATUS":"P16.21E_REAL_VIDEO_FETCH_LOOP_IMPLEMENTED",
        "SOURCES_SCANNED":len(load_sources()),
        "VIDEOS_FETCHED":len(all_rows),
        "ACTIONABLE_VIDEO_HYPOTHESES":len(actionable),
        "ERRORS":len(errors),
        "NEXT":"P16.21F_TRANSCRIPT_DOWNLOAD_AND_STRATEGY_EXTRACTION",
        **BLOCKS,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (OUT/"p1621e_video_metadata.json").write_text(json.dumps(all_rows,indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"p1621e_actionable_video_hypotheses.json").write_text(json.dumps(actionable,indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"p1621e_errors.json").write_text(json.dumps(errors,indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"p1621e_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    return report

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
