import csv, hashlib, json
from pathlib import Path
from datetime import datetime, UTC
from mind_trader.app.backtest.market_core import ingest_ohlcv_csv

ALIASES = {
    "ts": ["ts","time","datetime","date","data","timestamp","<date>","date_time"],
    "open": ["open","abertura","o","<open>"],
    "high": ["high","maxima","máxima","h","<high>"],
    "low": ["low","minima","mínima","l","<low>"],
    "close": ["close","fechamento","c","last","<close>"],
    "volume": ["volume","vol","tick_volume","real_volume","qty","quantidade","<tickvol>"]
}

def checksum(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):
            h.update(b)
    return h.hexdigest()

def detect_delimiter(path):
    sample=Path(path).read_text(encoding="utf-8-sig",errors="ignore")[:4096]
    return csv.Sniffer().sniff(sample, delimiters=",;\t").delimiter

def normalize_header(h):
    return str(h).strip().lower().replace(" ","_")

def map_columns(headers):
    norm=[normalize_header(x) for x in headers]
    mapped={}
    for target, names in ALIASES.items():
        for n in names:
            if normalize_header(n) in norm:
                mapped[target]=headers[norm.index(normalize_header(n))]
                break
    missing=[k for k in ALIASES if k not in mapped]
    if missing:
        raise ValueError(f"COLUNAS_OBRIGATORIAS_AUSENTES:{missing}")
    return mapped

def normalize_csv(input_path, output_path):
    delim=detect_delimiter(input_path)
    Path(output_path).parent.mkdir(parents=True,exist_ok=True)
    with open(input_path,"r",encoding="utf-8-sig",newline="") as f, open(output_path,"w",encoding="utf-8",newline="") as o:
        r=csv.DictReader(f,delimiter=delim)
        mp=map_columns(r.fieldnames or [])
        w=csv.DictWriter(o,fieldnames=["ts","open","high","low","close","volume"])
        w.writeheader()
        rows=0
        for x in r:
            w.writerow({
                "ts": str(x[mp["ts"]]).strip(),
                "open": float(str(x[mp["open"]]).replace(",",".")),
                "high": float(str(x[mp["high"]]).replace(",",".")),
                "low": float(str(x[mp["low"]]).replace(",",".")),
                "close": float(str(x[mp["close"]]).replace(",",".")),
                "volume": float(str(x[mp["volume"]]).replace(",","."))
            })
            rows+=1
    return {"normalized_path":str(output_path),"rows":rows,"checksum":checksum(input_path)}

def quality_report(normalized_csv_path, min_rows=90):
    seen=set(); duplicates=0; bad_ohlc=0; rows=[]; prev=None; gaps=0
    with open(normalized_csv_path,"r",encoding="utf-8",newline="") as f:
        r=csv.DictReader(f)
        for x in r:
            ts=x["ts"]
            o,h,l,c=map(float,[x["open"],x["high"],x["low"],x["close"]])
            if ts in seen: duplicates+=1
            seen.add(ts)
            if h < max(o,c) or l > min(o,c): bad_ohlc+=1
            if prev and ts <= prev: gaps+=1
            prev=ts
            rows.append(x)
    passed = len(rows) >= min_rows and duplicates == 0 and bad_ohlc == 0
    return {
        "rows":len(rows),
        "duplicates":duplicates,
        "bad_ohlc":bad_ohlc,
        "ordering_issues":gaps,
        "min_rows":min_rows,
        "quality_passed":passed,
        "decision":"ALLOW_BACKTEST" if passed else "BLOCK_BACKTEST"
    }

def ingest_with_quality_gate(input_path, symbol, timeframe, db_path="mind_trader/data/market.sqlite", normalized_dir="mind_trader/data/normalized"):
    raw_hash=checksum(input_path)
    out=Path(normalized_dir)/f"{symbol}_{timeframe}_{raw_hash[:12]}.csv"
    norm=normalize_csv(input_path,out)
    qr=quality_report(out)
    result={"source":str(input_path),"raw_checksum":raw_hash,"normalization":norm,"quality":qr,"ingestion":None,"ts":datetime.now(UTC).isoformat()}
    if not qr["quality_passed"]:
        result["decision"]="BLOCKED_DATA_QUALITY"
        return result
    result["ingestion"]=ingest_ohlcv_csv(out,symbol,timeframe,db_path)
    result["decision"]="INGESTED_AND_BACKTEST_ALLOWED"
    return result

def save_quality_report(report,path="mind_trader/reports/P8.29_quality_report.json"):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    return path
