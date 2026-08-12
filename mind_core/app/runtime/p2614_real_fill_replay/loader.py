import csv, pathlib
from datetime import datetime

def nf(k):
    return str(k).lower().strip().replace("<","").replace(">","").replace(" ","_")

def parse_dt(v):
    v=str(v or "").strip().replace("/", "-")
    for fmt in ["%Y.%m.%d %H:%M:%S","%Y-%m-%d %H:%M:%S","%Y-%m-%dT%H:%M:%S","%d-%m-%Y %H:%M:%S","%Y.%m.%d","%Y-%m-%d"]:
        try:
            return datetime.strptime(v[:19],fmt)
        except Exception:
            pass
    return None

def to_float(v):
    s=str(v).strip().replace(" ","")
    if s.count(",")==1 and s.count(".")==0:
        s=s.replace(",",".")
    return float(s)

def load_ohlc(path):
    path=pathlib.Path(path)
    sample=path.read_text(encoding="utf-8",errors="ignore")[:8192]
    delim=";" if sample.count(";") > sample.count(",") else ","
    candles=[]
    with open(path,encoding="utf-8",errors="ignore") as f:
        reader=csv.DictReader(f,delimiter=delim)
        for r in reader:
            low={nf(k):v for k,v in r.items() if k is not None}
            t=low.get("time") or low.get("datetime") or low.get("date") or low.get("timestamp") or low.get("data")
            dt=parse_dt(t)
            if not dt:
                continue
            try:
                o=to_float(low.get("open") or low.get("abertura"))
                h=to_float(low.get("high") or low.get("max") or low.get("maxima") or low.get("máxima"))
                l=to_float(low.get("low") or low.get("min") or low.get("minima") or low.get("mínima"))
                c=to_float(low.get("close") or low.get("fechamento") or low.get("last"))
            except Exception:
                continue
            if h>=max(o,c) and l<=min(o,c) and h>=l and c>0:
                candles.append({"time":dt,"open":o,"high":h,"low":l,"close":c})
    return sorted(candles,key=lambda x:x["time"])

def find_best_ger40_ohlc(root, evid):
    root=pathlib.Path(root)
    evid=pathlib.Path(evid)
    candidates=[]
    for base in [root/"mind_trader"/"data", root/"data", root, evid]:
        if not base.exists():
            continue
        for p in base.rglob("*.csv"):
            name=str(p).lower()
            if any(x in name for x in ["ger40","de40","dax","germany40"]) and any(x in name for x in ["m1","m5","m15","m30","h1","raw","ohlc","mt5","deep"]):
                try:
                    candles=load_ohlc(p)
                    if len(candles)>=500:
                        candidates.append((len(candles),str(p),candles))
                except Exception:
                    pass
    if not candidates:
        raise RuntimeError("NO_VALID_GER40_OHLC_FOUND")
    candidates.sort(key=lambda x:x[0],reverse=True)
    return candidates[0]
