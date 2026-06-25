import csv, json, math, statistics
from pathlib import Path
from datetime import datetime
from collections import defaultdict

MODE="PAPER_ONLY"
REAL_ORDERS="FORBIDDEN"
FTMO_REAL="FORBIDDEN"

TIMEFRAME_FILES={
    "M1":"mind_ger40_5y_p2363b_DE40_M1_csv",
    "M5":"mind_ger40_5y_p2363b_DE40_M5_csv",
    "M15":"mind_ger40_5y_p2363b_DE40_M15_csv",
    "M30":"mind_ger40_5y_p2363b_DE40_M30_csv",
    "H1":"mind_ger40_5y_p2363b_DE40_H1_csv",
    "H4":"mind_ger40_5y_p2363b_DE40_H4_csv",
    "D1":"mind_ger40_5y_p2363b_DE40_D1_csv",
}

DATE_FORMATS=[
    "%Y.%m.%d %H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d",
    "%d/%m/%Y %H:%M:%S",
    "%d/%m/%Y",
]

ATR_PERIOD=14
MIN_ATR_FLOOR_BY_TF={
    "M1": 2.0,
    "M5": 4.0,
    "M15": 8.0,
    "M30": 12.0,
    "H1": 18.0,
    "H4": 35.0,
    "D1": 80.0,
}
MAX_ABS_R=10.0

def safety():
    assert MODE=="PAPER_ONLY"
    assert REAL_ORDERS=="FORBIDDEN"
    assert FTMO_REAL=="FORBIDDEN"

def fnum(x):
    try:
        if x is None or str(x).strip()=="":
            return 0.0
        return float(str(x).replace(",","."))
    except Exception:
        return 0.0

def parse_time(x):
    s=str(x).strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(s[:19],fmt)
        except Exception:
            pass
    return datetime.min

def read_csv_auto(path):
    with open(path,"r",encoding="utf-8-sig",newline="") as f:
        sample=f.read(4096)
        f.seek(0)
        delimiter=";" if sample.count(";")>=sample.count(",") else ","
        return list(csv.DictReader(f,delimiter=delimiter))

def write_csv(path, rows, fields):
    with open(path,"w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k:r.get(k,"") for k in fields})

def normalize(row):
    return {
        "time":row.get("time",""),
        "dt":parse_time(row.get("time","")),
        "open":fnum(row.get("open")),
        "high":fnum(row.get("high")),
        "low":fnum(row.get("low")),
        "close":fnum(row.get("close")),
        "tick_volume":fnum(row.get("tick_volume")),
        "spread":fnum(row.get("spread")),
        "symbol":row.get("symbol","DE40"),
        "timeframe":row.get("timeframe","")
    }

def true_range(c, prev):
    if not prev:
        return max(c["high"]-c["low"],0.0)
    return max(
        c["high"]-c["low"],
        abs(c["high"]-prev["close"]),
        abs(c["low"]-prev["close"])
    )

def add_atr(candles, tf):
    candles=sorted(candles,key=lambda x:x["dt"])
    trs=[]
    for i,c in enumerate(candles):
        prev=candles[i-1] if i>0 else None
        tr=true_range(c,prev)
        trs.append(tr)
        if i < ATR_PERIOD:
            c["atr"]=0.0
        else:
            raw=sum(trs[i-ATR_PERIOD+1:i+1])/ATR_PERIOD
            c["atr"]=max(raw, MIN_ATR_FLOOR_BY_TF.get(tf,1.0))
    return candles

def split_80_20(rows):
    rows=sorted(rows,key=lambda x:x["dt"])
    cut=math.floor(len(rows)*0.80)
    return rows[:cut], rows[cut:]

def regime(c, prev):
    if not prev:
        return "UNKNOWN"
    rng=max(c["high"]-c["low"],0.000001)
    body=abs(c["close"]-c["open"])
    delta=c["close"]-prev["close"]
    body_ratio=body/rng
    if body_ratio < 0.25:
        return "ACCUMULATION"
    if body_ratio >= 0.55 and delta > 0:
        return "MARKUP"
    if body_ratio >= 0.55 and delta < 0:
        return "MARKDOWN"
    return "DISTRIBUTION"

def session(dt):
    h=dt.hour
    if 1 <= h < 8:
        return "ASIA_EARLY_EUROPE"
    if 8 <= h < 12:
        return "EUROPE_OPEN"
    if 12 <= h < 16:
        return "EUROPE_US_OVERLAP"
    if 16 <= h < 21:
        return "US_AFTERNOON"
    return "LOW_LIQUIDITY"

def footprint(c, prev):
    if not prev:
        return "UNKNOWN"
    rng=max(c["high"]-c["low"],0.000001)
    prev_rng=max(prev["high"]-prev["low"],0.000001)
    body=abs(c["close"]-c["open"])
    if c["high"] > prev["high"] and c["close"] < prev["high"]:
        return "LIQUIDITY_SWEEP_HIGH"
    if c["low"] < prev["low"] and c["close"] > prev["low"]:
        return "LIQUIDITY_SWEEP_LOW"
    if rng > prev_rng * 1.8 and body/rng > 0.55:
        return "DISPLACEMENT"
    return "NORMAL_FLOW"

def lifecycle(c, prev):
    if not prev:
        return "UNKNOWN"
    if c["close"] > prev["high"]:
        return "CONTINUATION_UP"
    if c["close"] < prev["low"]:
        return "CONTINUATION_DOWN"
    if c["high"] > prev["high"] and c["close"] < prev["close"]:
        return "REVERSAL_DOWN"
    if c["low"] < prev["low"] and c["close"] > prev["close"]:
        return "REVERSAL_UP"
    return "PULLBACK_OR_BALANCE"

def clamp(x):
    if x > MAX_ABS_R:
        return MAX_ABS_R
    if x < -MAX_ABS_R:
        return -MAX_ABS_R
    return x

def simulate(c, prev, nxt, tf):
    if not prev or not nxt:
        return None

    atr=max(c.get("atr",0.0), MIN_ATR_FLOOR_BY_TF.get(tf,1.0))
    candle_range=c["high"]-c["low"]

    if atr <= 0:
        return None
    if candle_range <= 0:
        return None

    direction=1 if c["close"] >= c["open"] else -1
    move=(nxt["close"]-c["close"])*direction
    raw_r=move/atr
    clipped_r=clamp(raw_r)

    return {
        "entry_time":c["time"],
        "family":"OOS_ATR_NORMALIZED_CONTEXT_PROXY",
        "footprint":footprint(c,prev),
        "lifecycle":lifecycle(c,prev),
        "regime":regime(c,prev),
        "session":session(c["dt"]),
        "timeframe":tf,
        "atr":round(atr,6),
        "candle_range":round(candle_range,6),
        "raw_r":round(raw_r,6),
        "realized_r":round(clipped_r,6),
        "mae_r":0,
        "mfe_r":round(abs(clipped_r),6),
        "rr_realized":round(clipped_r,6),
        "profit_factor_proxy":0,
        "expectancy_r_proxy":round(clipped_r,6),
        "clipped":abs(raw_r)>MAX_ABS_R
    }

def metrics(rows):
    n=len(rows)
    rs=[fnum(r.get("realized_r")) for r in rows]
    wins=[x for x in rs if x>0]
    losses=[x for x in rs if x<0]
    gw=sum(wins)
    gl=abs(sum(losses))
    pf=999.0 if gl==0 and gw>0 else (gw/gl if gl>0 else 0.0)
    exp=sum(rs)/n if n else 0.0
    wr=len(wins)/n*100.0 if n else 0.0
    eq=0.0
    peak=0.0
    dd=0.0
    for r in rs:
        eq += r
        peak=max(peak,eq)
        dd=max(dd,peak-eq)
    return {
        "samples":n,
        "wins":len(wins),
        "losses":len(losses),
        "winrate":round(wr,6),
        "pf":round(pf,6),
        "expectancy":round(exp,6),
        "max_dd_r":round(dd,6),
        "gross_win":round(gw,6),
        "gross_loss":round(gl,6)
    }

def gate(m):
    return m["samples"]>=30 and m["pf"]>=1.5 and m["expectancy"]>0 and m["winrate"]>=45

def stability(signals, dim):
    d=defaultdict(list)
    for s in signals:
        d[s.get(dim,"UNKNOWN")].append(s)
    out=[]
    for k,v in sorted(d.items()):
        m=metrics(v)
        out.append({"dimension":dim,"value":k,**m,"passed":gate(m)})
    return out

def run(dataset, previous, outdir):
    safety()
    out=Path(outdir)
    out.mkdir(parents=True,exist_ok=True)

    all_signals=[]
    tf_results=[]
    audit=[]
    outliers=[]

    for tf,file in TIMEFRAME_FILES.items():
        path=Path(dataset)/file
        if not path.exists():
            raise FileNotFoundError(str(path))

        raw=read_csv_auto(path)
        normalized=[normalize(r) for r in raw]
        valid=[c for c in normalized if c["dt"]!=datetime.min and c["open"]>0 and c["high"]>0 and c["low"]>0 and c["close"]>0]
        valid=add_atr(valid,tf)

        train,oos=split_80_20(valid)

        signals=[]
        skipped_atr_warmup=0
        skipped_degenerate=0

        for i in range(1,len(oos)-1):
            if oos[i].get("atr",0.0)<=0:
                skipped_atr_warmup+=1
                continue
            if oos[i]["high"]-oos[i]["low"]<=0:
                skipped_degenerate+=1
                continue

            sig=simulate(oos[i],oos[i-1],oos[i+1],tf)
            if sig:
                signals.append(sig)
                if sig["clipped"]:
                    outliers.append(sig)

        m=metrics(signals)
        tf_results.append({
            "timeframe":tf,
            "file":str(path),
            "raw_rows":len(raw),
            "valid_candles":len(valid),
            "train_candles":len(train),
            "oos_candles":len(oos),
            "signals":len(signals),
            "skipped_atr_warmup":skipped_atr_warmup,
            "skipped_degenerate":skipped_degenerate,
            "clipped_outliers":len([s for s in signals if s["clipped"]]),
            **m,
            "passed":gate(m)
        })

        audit.append({
            "timeframe":tf,
            "first_time":valid[0]["time"] if valid else "",
            "last_time":valid[-1]["time"] if valid else "",
            "oos_start":oos[0]["time"] if oos else "",
            "oos_end":oos[-1]["time"] if oos else "",
            "valid_candles":len(valid),
            "oos_candles":len(oos),
            "signals":len(signals),
            "atr_floor":MIN_ATR_FLOOR_BY_TF.get(tf,1.0)
        })

        all_signals.extend(signals)
        write_csv(out/f"de40_oos_atr_signals_{tf}.csv",signals,list(signals[0].keys()) if signals else ["entry_time"])

    promoted=[r for r in tf_results if r["passed"]]
    rejected=[r for r in tf_results if not r["passed"]]
    global_m=metrics(all_signals)

    write_csv(out/"de40_oos_atr_dataset_audit.csv",audit,list(audit[0].keys()))
    write_csv(out/"de40_oos_atr_all_signals.csv",all_signals,list(all_signals[0].keys()) if all_signals else ["entry_time"])
    write_csv(out/"de40_oos_atr_timeframe_results.csv",tf_results,list(tf_results[0].keys()))
    write_csv(out/"de40_oos_atr_promoted.csv",promoted,list(tf_results[0].keys()))
    write_csv(out/"de40_oos_atr_rejected.csv",rejected,list(tf_results[0].keys()))
    write_csv(out/"de40_oos_atr_outliers_clipped.csv",outliers,list(outliers[0].keys()) if outliers else ["entry_time"])

    for dim in ["regime","session","footprint","lifecycle","timeframe"]:
        rows=stability(all_signals,dim)
        write_csv(out/f"de40_oos_atr_{dim}_stability.csv",rows,list(rows[0].keys()) if rows else ["dimension"])

    summary={
        "mission":"P2383C2_RISK_NORMALIZATION_REPAIR",
        "mode":MODE,
        "real_orders":REAL_ORDERS,
        "ftmo_real":FTMO_REAL,
        "dataset":str(dataset),
        "previous_p2383c_fix":str(previous),
        "output":str(out),
        "repair":"ATR-normalized R, zero-range candle block, ATR floor by timeframe, max absolute R clamp.",
        "atr_period":ATR_PERIOD,
        "max_abs_r":MAX_ABS_R,
        "atr_floor_by_timeframe":MIN_ATR_FLOOR_BY_TF,
        "global_metrics":global_m,
        "timeframes_tested":len(tf_results),
        "promoted":len(promoted),
        "rejected":len(rejected),
        "clipped_outliers":len(outliers),
        "certification":"OOS_ATR_PROXY_PROMOTED" if len(promoted)>0 else "OOS_ATR_PROXY_NOT_PROMOTED",
        "original_p2382_edge_certified":False,
        "p2384_allowed":False,
        "next_required":"P2383D_EXACT_PLAYBOOK_TO_RAW_CANDLE_VALIDATOR"
    }

    with open(out/"summary.json","w",encoding="utf-8") as f:
        json.dump(summary,f,indent=2,ensure_ascii=False)

    return summary

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--dataset",required=True)
    p.add_argument("--previous",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    print(json.dumps(run(a.dataset,a.previous,a.out),indent=2,ensure_ascii=False))
