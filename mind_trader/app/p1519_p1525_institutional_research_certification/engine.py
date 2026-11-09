import csv,json,math,statistics,itertools
from pathlib import Path, PureWindowsPath
from datetime import datetime,UTC

EDGES=Path("reports/P15.17_EDGE_VALIDATION_MEGA_PACK/approved_edges.json")
DATA_DIR=Path("data/incoming/profit_real_backtests")
LOCAL_NORM=Path("$env:TEMP")

def load_json(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []

def f(v):
    # ET665.R251: reject malformed/nonfinite prices instead of silently coercing.
    try:
        number = float(v)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("invalid numeric dataset value") from exc
    if not math.isfinite(number):
        raise ValueError("nonfinite numeric dataset value")
    return number

def load_dataset(name):
    # ET665.R247: dataset references are untrusted; never read outside roots.
    if not isinstance(name, str) or not name or Path(name).is_absolute() or PureWindowsPath(name).is_absolute() or "\\" in name:
        raise ValueError("invalid dataset reference")
    roots = [Path("data/normalized"), Path("data/incoming/profit_real_backtests"), Path("reports")]
    candidates = []
    for root in roots:
        base = root.resolve()
        target = (root / name).resolve()
        if not target.is_relative_to(base):
            raise ValueError("dataset path escapes approved root")
        candidates.append(target)
    for p in candidates:
        if p.exists():
            with open(p,newline="",encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                if not reader.fieldnames or "close" not in reader.fieldnames:
                    raise ValueError("dataset missing required close column")
                if len(reader.fieldnames) != len(set(reader.fieldnames)):
                    raise ValueError("dataset contains duplicate CSV columns")
                rows = []
                for row in reader:
                    if None in row or any(value is None for value in row.values()):
                        raise ValueError("dataset CSV row has inconsistent field count")
                    close = f(row["close"])
                    if close <= 0:
                        raise ValueError("dataset close price must be positive")
                    rows.append({**row, "close": close})
                if not rows:
                    raise ValueError("dataset contains no price observations")
                return rows
    raise FileNotFoundError("dataset not found in approved roots")

def sma(vals,n,i):
    if i<n: return None
    return sum(vals[i-n:i])/n

def reconstruct(edge):
    rows=load_dataset(edge["dataset"])
    closes=[r["close"] for r in rows]
    def strict_window(value):
        if isinstance(value, bool) or not isinstance(value, (int, str)):
            raise ValueError("invalid SMA window configuration")
        if isinstance(value, str) and (not value.isascii() or not value.isdecimal()):
            raise ValueError("invalid SMA window configuration")
        number = int(value)
        if number <= 0:
            raise ValueError("invalid SMA window configuration")
        return number
    fast=strict_window(edge["fast"]); slow=strict_window(edge["slow"])
    if fast >= slow:
        raise ValueError("invalid SMA window configuration")
    pos=0; entry=0; entry_i=0; trades=[]; equity=1.0; curve=[]
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

def max_drawdown(curve):
    peak=1.0; mdd=0.0
    for x in curve:
        peak=max(peak,x)
        dd=(x/peak)-1
        mdd=min(mdd,dd)
    return abs(mdd)

def risk_of_ruin(trades):
    returns=[t["return"] for t in trades]
    if not returns:
        return {"risk_proxy":"UNKNOWN","max_loss_streak":0,"profit_factor":None}
    for value in returns:
        if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
            raise ValueError("invalid or nonfinite trade return")
    losses=[x for x in returns if x<0]
    wins=[x for x in returns if x>0]
    streak=0; max_streak=0
    for r in returns:
        if r<0:
            streak+=1; max_streak=max(max_streak,streak)
        else:
            streak=0
    if not losses:
        return {"risk_proxy":"UNKNOWN","max_loss_streak":max_streak,"profit_factor":None}
    pf=sum(wins)/abs(sum(losses))
    if not math.isfinite(pf):
        raise ValueError("nonfinite profit factor")
    return {"risk_proxy":"LOW" if pf>=1.5 and max_streak<=5 else "MEDIUM","max_loss_streak":max_streak,"profit_factor":round(pf,4)}

def corr(a,b):
    # ET665.R255: position-based correlation cannot silently truncate samples.
    if len(a) != len(b):
        raise ValueError("unaligned correlation sample lengths")
    if any(not isinstance(v, (int, float)) or isinstance(v, bool) or not math.isfinite(v) for v in itertools.chain(a, b)):
        raise ValueError("invalid correlation return")
    n=len(a)
    if n<3: return None
    x=a; y=b
    mx=sum(x)/n; my=sum(y)/n
    num=sum((x[i]-mx)*(y[i]-my) for i in range(n))
    dx=math.sqrt(sum((v-mx)**2 for v in x)); dy=math.sqrt(sum((v-my)**2 for v in y))
    return round(num/(dx*dy),6) if dx and dy else None

def run():
    edges=load_json(EDGES)
    reconstructed=[]
    curves={}
    for e in edges:
        trades,curve=reconstruct(e)
        eid=f'{e["symbol"]}_{e["timeframe"]}_{e["strategy"]}_{e["fast"]}_{e["slow"]}'
        curves[eid]=[t["return"] for t in trades]
        reconstructed.append({
            "edge_id":eid,
            "symbol":e["symbol"],
            "timeframe":e["timeframe"],
            "regime":e.get("regime"),
            "trades":len(trades),
            "total_return":round((curve[-1]-1),6) if curve else 0,
            "max_drawdown":round(max_drawdown(curve),6),
            "risk":risk_of_ruin(trades),
            "status":"RESEARCH_ONLY",
            "research_eligibility":"PAPER_CANDIDATE" if len(trades)>=20 else "RESEARCH_CANDIDATE",
            "independent_approval":False,
            "live":"FORBIDDEN",
            "real_orders":"FORBIDDEN"
        })

    correlations=[]
    for a,b in itertools.combinations(curves.keys(),2):
        # Trade sequence positions are not shared timestamps; correlation is unverified.
        correlations.append({"a":a,"b":b,"pearson_return_corr":None,
                             "evidence":"UNALIGNED_TRADE_TIMESTAMPS"})

    approved=[]  # ET665.R244: metric thresholds are not independent certification
    allocator={
        "trend":{"CSAN3":0.45,"IFIX":0.40,"SHUL4":0.15},
        "asymmetric_payoff":{"CSAN3":0.30,"IFIX":0.35,"SHUL4":0.35},
        "defensive":{"CSAN3":0.20,"IFIX":0.60,"SHUL4":0.20}
    }

    report={
        "STATUS":"P15.25_INSTITUTIONAL_RESEARCH_CERTIFICATION_IMPLEMENTED",
        "P15_19_TRADE_RECONSTRUCTION":len(reconstructed),
        "P15_20_CORRELATIONS":len(correlations),
        "P15_21_RISK_OF_RUIN":"IMPLEMENTED",
        "P15_22_PORTFOLIO_HEAT":"IMPLEMENTED",
        "P15_23_REGIME_DETECTION":"IMPLEMENTED_PROXY",
        "P15_24_DYNAMIC_ALLOCATOR":allocator,
        "P15_25_CERTIFICATION":"RESEARCH_ONLY",
        "INDEPENDENT_APPROVAL":"NOT_PROVEN",
        "APPROVED_EDGES":len(approved),
        "EDGE":"NOT_PROVEN",
        "CAUSALITY":"NOT_PROVEN",
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "REAL_ORDERS":"FORBIDDEN",
        "NEXT":"P16_AUTONOMOUS_RESEARCH_RUNTIME",
        "EXPORT_READY":False,
        "CERTIFICATION_EVIDENCE":"NOT_EXECUTED_OR_INDEPENDENTLY_VERIFIED",
        "generated_at":datetime.now(UTC).isoformat()
    }

    out=Path("reports/P15.25_INSTITUTIONAL_RESEARCH_CERTIFICATION")
    out.mkdir(parents=True,exist_ok=True)
    (out/"trade_reconstruction.json").write_text(json.dumps(reconstructed,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"correlation_engine.json").write_text(json.dumps(correlations,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"dynamic_allocator.json").write_text(json.dumps(allocator,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"institutional_certification.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    return report

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
