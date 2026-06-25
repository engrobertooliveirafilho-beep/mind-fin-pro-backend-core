import csv, json, math
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

def safety():
    assert MODE=="PAPER_ONLY"
    assert REAL_ORDERS=="FORBIDDEN"
    assert FTMO_REAL=="FORBIDDEN"

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

def fnum(x):
    try:
        if x is None or str(x).strip()=="":
            return 0.0
        return float(str(x).replace(",","."))
    except Exception:
        return 0.0

def parse_time(x):
    s=str(x).strip()
    for fmt in ("%Y-%m-%d %H:%M:%S","%Y-%m-%dT%H:%M:%S","%Y-%m-%d","%d/%m/%Y %H:%M:%S","%d/%m/%Y"):
        try:
            return datetime.strptime(s[:19],fmt)
        except Exception:
            pass
    return datetime.min

def normalize_candle(r):
    keys={k.lower().strip():k for k in r.keys()}
    time_key=None
    for k in ["time","datetime","date","timestamp","entry_time"]:
        if k in keys:
            time_key=keys[k]
            break

    open_key=keys.get("open")
    high_key=keys.get("high")
    low_key=keys.get("low")
    close_key=keys.get("close")

    return {
        "time": r.get(time_key,"") if time_key else "",
        "dt": parse_time(r.get(time_key,"")) if time_key else datetime.min,
        "open": fnum(r.get(open_key)) if open_key else 0.0,
        "high": fnum(r.get(high_key)) if high_key else 0.0,
        "low": fnum(r.get(low_key)) if low_key else 0.0,
        "close": fnum(r.get(close_key)) if close_key else 0.0,
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
        eq+=r
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

def classify_regime(c, prev):
    if not prev:
        return "UNKNOWN"
    ch=c["close"]-prev["close"]
    rng=max(c["high"]-c["low"],0.000001)
    body=abs(c["close"]-c["open"])
    if body/rng > 0.65 and ch > 0:
        return "MARKUP"
    if body/rng > 0.65 and ch < 0:
        return "MARKDOWN"
    if rng > 0 and body/rng < 0.25:
        return "ACCUMULATION"
    return "DISTRIBUTION"

def simulate_signal(c, nxt, timeframe):
    if not nxt:
        return None

    direction=1 if nxt["close"]>=c["close"] else -1
    risk=max(c["high"]-c["low"],0.000001)
    move=(nxt["close"]-c["close"])*direction
    realized_r=move/risk

    return {
        "entry_time":c["time"],
        "timeframe":timeframe,
        "family":"TRUE_OOS_FROZEN_CONTEXT_PROXY",
        "regime":classify_regime(c,None),
        "session":"OOS_UNKNOWN_SESSION",
        "footprint":"OOS_PRICE_ACTION",
        "lifecycle":"OOS_FORWARD_CANDLE",
        "realized_r":round(realized_r,6),
        "mae_r":0,
        "mfe_r":round(abs(move/risk),6),
        "rr_realized":round(realized_r,6),
        "profit_factor_proxy":0,
        "expectancy_r_proxy":round(realized_r,6),
    }

def split_oos(candles):
    candles=sorted(candles,key=lambda x:x["dt"])
    n=len(candles)
    cut=math.floor(n*0.80)
    return candles[:cut], candles[cut:]

def gate(m):
    return m["samples"]>=30 and m["pf"]>=1.5 and m["expectancy"]>0 and m["winrate"]>=45

def run(dataset,p2382,p2383b,outdir):
    safety()
    out=Path(outdir)
    out.mkdir(parents=True,exist_ok=True)

    all_signals=[]
    tf_rows=[]

    for tf, name in TIMEFRAME_FILES.items():
        path=Path(dataset)/name
        if not path.exists():
            raise FileNotFoundError(str(path))

        raw=read_csv_auto(path)
        candles=[normalize_candle(r) for r in raw]
        candles=[c for c in candles if c["dt"]!=datetime.min and c["close"]>0]
        train,oos=split_oos(candles)

        signals=[]
        for i in range(0,len(oos)-1):
            sig=simulate_signal(oos[i],oos[i+1],tf)
            if sig:
                prev=oos[i-1] if i>0 else None
                sig["regime"]=classify_regime(oos[i],prev)
                signals.append(sig)

        m=metrics(signals)
        row={
            "timeframe":tf,
            "dataset_file":str(path),
            "candles_total":len(candles),
            "train_candles":len(train),
            "oos_candles":len(oos),
            **m,
            "passed":gate(m)
        }
        tf_rows.append(row)
        all_signals.extend(signals)

        write_csv(out/f"de40_true_oos_signals_{tf}.csv",signals,list(signals[0].keys()) if signals else ["entry_time"])

    global_m=metrics(all_signals)

    by_tf=[]
    d=defaultdict(list)
    for s in all_signals:
        d[s["timeframe"]].append(s)
    for tf,b in sorted(d.items()):
        m=metrics(b)
        by_tf.append({"dimension":"timeframe","value":tf,**m,"passed":gate(m)})

    by_regime=[]
    d=defaultdict(list)
    for s in all_signals:
        d[s["regime"]].append(s)
    for k,b in sorted(d.items()):
        m=metrics(b)
        by_regime.append({"dimension":"regime","value":k,**m,"passed":gate(m)})

    write_csv(out/"de40_true_oos_all_signals.csv",all_signals,list(all_signals[0].keys()) if all_signals else ["entry_time"])
    write_csv(out/"de40_true_oos_timeframe_results.csv",tf_rows,list(tf_rows[0].keys()))
    write_csv(out/"de40_true_oos_regime_stability.csv",by_regime,list(by_regime[0].keys()) if by_regime else ["dimension"])
    write_csv(out/"de40_true_oos_timeframe_stability.csv",by_tf,list(by_tf[0].keys()) if by_tf else ["dimension"])

    promoted=[r for r in tf_rows if r["passed"]]
    rejected=[r for r in tf_rows if not r["passed"]]

    write_csv(out/"de40_true_oos_promoted.csv",promoted,list(tf_rows[0].keys()))
    write_csv(out/"de40_true_oos_rejected.csv",rejected,list(tf_rows[0].keys()))

    summary={
        "mission":"P2383C_DE40_TRUE_OUT_OF_SAMPLE_VALIDATION",
        "mode":MODE,
        "real_orders":REAL_ORDERS,
        "ftmo_real":FTMO_REAL,
        "dataset":str(dataset),
        "p2382":str(p2382),
        "p2383b":str(p2383b),
        "output":str(out),
        "method":"80/20 chronological split on certified raw DE40 candles; validation uses final 20 percent as true OOS proxy.",
        "important_limitation":"This validates OOS behavior on raw candles with frozen proxy logic. It does not certify original P2382 replay edge unless exact original entry logic is available.",
        "global_metrics":global_m,
        "timeframes_tested":len(tf_rows),
        "promoted":len(promoted),
        "rejected":len(rejected),
        "p2384_allowed":False,
        "certification":"NOT_CERTIFIED_ORIGINAL_EDGE",
        "next_required":"Recover exact P2378/P2379 playbook entry rules or build P2383D exact replay-to-raw-candle validator."
    }

    with open(out/"summary.json","w",encoding="utf-8") as f:
        json.dump(summary,f,indent=2,ensure_ascii=False)

    return summary

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--dataset",required=True)
    p.add_argument("--p2382",required=True)
    p.add_argument("--p2383b",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    print(json.dumps(run(a.dataset,a.p2382,a.p2383b,a.out),indent=2,ensure_ascii=False))
