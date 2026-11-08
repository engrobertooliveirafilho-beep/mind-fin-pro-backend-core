import csv,json,math,statistics,itertools,subprocess,os,shutil
from pathlib import Path, PureWindowsPath
from datetime import datetime,UTC

EDGES=Path("reports/P15.17_EDGE_VALIDATION_MEGA_PACK/approved_edges.json")
REMOTE_NORM="gdrive:mind-workspace/MIND_TRADER/P15_REAL_MARKET_DATA/normalized"
REMOTE_REPORTS="gdrive:mind-workspace/MIND_TRADER/P15_REAL_MARKET_DATA/reports/P15.25B"
TMP=Path(os.environ.get("TEMP",".")).joinpath("mind_p1525b_reconstruction")
DATA=TMP/"normalized"

def cmd(c):
    # ET665.CM.2: allow read-only rclone with argv; prohibit historic Drive writes.
    import shlex
    args = shlex.split(c)
    if len(args) < 4 or args[:2] != ["rclone", "copy"] or not args[2].startswith("gdrive:") or any(a.startswith("gdrive:") for a in args[3:]):
        raise PermissionError("ET665_DRIVE_HISTORICAL_WRITE_FORBIDDEN")
    return subprocess.run(args, shell=False, capture_output=True, text=True, check=True)

def load_json(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []

def safe_dataset_path(name):
    # Dataset metadata is untrusted: keep reads inside the normalized staging root.
    if not isinstance(name, str) or not name.strip() or "\x00" in name:
        raise PermissionError("ET665_INVALID_DATASET_PATH")
    relative = Path(name)
    windows_relative = PureWindowsPath(name)
    if (relative.is_absolute() or bool(relative.drive) or windows_relative.is_absolute()
            or bool(windows_relative.drive) or ".." in relative.parts
            or ".." in windows_relative.parts):
        raise PermissionError("ET665_DATASET_PATH_ESCAPE_BLOCKED")
    if DATA.is_symlink():
        raise PermissionError("ET665_DATASET_ROOT_SYMLINK_BLOCKED")
    root = DATA.resolve()
    candidate = (root / relative).resolve()
    if candidate == root or root not in candidate.parents:
        raise PermissionError("ET665_DATASET_PATH_ESCAPE_BLOCKED")
    current = DATA
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise PermissionError("ET665_DATASET_SYMLINK_BLOCKED")
    if candidate.exists() and not candidate.is_file():
        raise PermissionError("ET665_DATASET_NOT_FILE")
    return candidate

def f(v):
    try: return float(v)
    except: return 0.0

def load_dataset(name):
    p=safe_dataset_path(name)
    if not p.exists():
        return []
    with open(p,newline="",encoding="utf-8") as fh:
        return [{**r,"close":f(r.get("close",0))} for r in csv.DictReader(fh) if f(r.get("close",0))>0]

def sma(vals,n,i):
    if i<n: return None
    return sum(vals[i-n:i])/n

def reconstruct(edge):
    rows=load_dataset(edge["dataset"])
    closes=[r["close"] for r in rows]
    fast=int(edge["fast"]); slow=int(edge["slow"])
    pos=0; entry=0; entry_i=0; trades=[]; equity=1.0; curve=[1.0]
    for i in range(slow+1,len(closes)):
        f0=sma(closes,fast,i); s0=sma(closes,slow,i)
        f1=sma(closes,fast,i-1); s1=sma(closes,slow,i-1)
        if None in (f0,s0,f1,s1): continue
        if pos==0 and f0>s0 and f1<=s1:
            pos=1; entry=closes[i]; entry_i=i
        elif pos==1 and f0<s0 and f1>=s1:
            ret=(closes[i]/entry)-1
            equity*=1+ret
            trades.append({"entry_index":entry_i,"exit_index":i,"entry_price":entry,"exit_price":closes[i],"return":ret,"equity":equity})
            curve.append(equity)
            pos=0
    if pos==1 and closes:
        ret=(closes[-1]/entry)-1
        equity*=1+ret
        trades.append({"entry_index":entry_i,"exit_index":len(closes)-1,"entry_price":entry,"exit_price":closes[-1],"return":ret,"equity":equity})
        curve.append(equity)
    return trades,curve

def metrics(trades,curve):
    returns=[t["return"] for t in trades]
    wins=[x for x in returns if x>0]; losses=[x for x in returns if x<=0]
    gross_win=sum(wins); gross_loss=abs(sum(losses))
    pf=gross_win/gross_loss if gross_loss else (99 if gross_win else 0)
    peak=1.0; mdd=0.0
    for x in curve:
        peak=max(peak,x)
        mdd=min(mdd,(x/peak)-1)
    streak=0; max_streak=0
    for r in returns:
        if r<0:
            streak+=1; max_streak=max(max_streak,streak)
        else:
            streak=0
    total=curve[-1]-1 if curve else 0
    recovery=total/abs(mdd) if mdd else 0
    return {
        "trades":len(trades),
        "profit_factor":round(pf,6),
        "total_return":round(total,6),
        "max_drawdown":round(abs(mdd),6),
        "recovery_factor":round(recovery,6),
        "winrate":round((len(wins)/len(returns))*100,4) if returns else 0,
        "max_loss_streak":max_streak
    }

def corr(a,b):
    n=min(len(a),len(b))
    if n<3: return 0
    x=a[:n]; y=b[:n]
    mx=sum(x)/n; my=sum(y)/n
    num=sum((x[i]-mx)*(y[i]-my) for i in range(n))
    dx=math.sqrt(sum((v-mx)**2 for v in x)); dy=math.sqrt(sum((v-my)**2 for v in y))
    return round(num/(dx*dy),6) if dx and dy else 0

def safe_cleanup():
    expected = Path(os.environ.get("TEMP", ".")).resolve()
    if TMP.resolve() != expected / "mind_p1525b_reconstruction" or TMP.resolve() == Path.cwd().resolve():
        raise PermissionError("ET665_UNSAFE_TEMP_PATH")
    if TMP.exists():
        shutil.rmtree(TMP)

def run():
    if TMP.exists(): safe_cleanup()
    DATA.mkdir(parents=True,exist_ok=True)
    cmd(f'rclone copy "{REMOTE_NORM}" "{DATA}" --progress')

    edges=load_json(EDGES)
    reconstructed=[]
    return_series={}
    trade_logs={}

    for e in edges:
        trades,curve=reconstruct(e)
        eid=f'{e["symbol"]}_{e["timeframe"]}_{e["strategy"]}_{e["fast"]}_{e["slow"]}'
        m=metrics(trades,curve)
        status="PAPER_RESEARCH_CERTIFIED" if m["trades"]>=20 and m["profit_factor"]>=1.25 and m["recovery_factor"]>=1 else "RESEARCH_ONLY"
        reconstructed.append({
            "edge_id":eid,
            "dataset":e["dataset"],
            "symbol":e["symbol"],
            "timeframe":e["timeframe"],
            "regime":e.get("regime"),
            **m,
            "status":status,
            "live":"FORBIDDEN",
            "real_orders":"FORBIDDEN"
        })
        return_series[eid]=[t["return"] for t in trades]
        trade_logs[eid]=trades

    correlations=[]
    for a,b in itertools.combinations(return_series.keys(),2):
        correlations.append({"a":a,"b":b,"pearson_trade_return_corr":corr(return_series[a],return_series[b])})

    approved=[x for x in reconstructed if x["status"]=="PAPER_RESEARCH_CERTIFIED"]

    out=Path("reports/P15.25B_CLOUD_DATASET_RECONSTRUCTION_FIX")
    out.mkdir(parents=True,exist_ok=True)

    report={
        "STATUS":"P15.25B_CLOUD_DATASET_RECONSTRUCTION_FIX_IMPLEMENTED",
        "CLOUD_DATA_SOURCE":REMOTE_NORM,
        "EDGES_RECONSTRUCTED":len(reconstructed),
        "APPROVED_EDGES":len(approved),
        "CORRELATIONS":len(correlations),
        "CERTIFICATION":"PAPER_RESEARCH_CERTIFIED" if approved else "RESEARCH_ONLY",
        "EDGE":"PAPER_RESEARCH_CERTIFIED" if approved else "NOT_PROVEN",
        "CAUSALITY":"NOT_PROVEN",
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "REAL_ORDERS":"FORBIDDEN",
        "NEXT":"P16_AUTONOMOUS_RESEARCH_RUNTIME",
        "EXPORT_READY":True,
        "generated_at":datetime.now(UTC).isoformat()
    }

    (out/"trade_reconstruction_cloud.json").write_text(json.dumps(reconstructed,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"trade_logs.json").write_text(json.dumps(trade_logs,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"correlations_cloud.json").write_text(json.dumps(correlations,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"institutional_certification_cloud_fix.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")

    from mind_trader.security.et665_cm6_evidence_stager import stage_engine_report
    stage_engine_report(out, "p1525b")  # Offline only; GitHub publication requires review.
    safe_cleanup()
    return report

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
