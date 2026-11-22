from pathlib import Path
import csv,json

EV=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core\\_evidence\\P2297_REAL_EXIT_FINAL_SEGMENT_WF_20260621_233649")
INPUT=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core\\_evidence\\P2296F_REAL_EXIT_DEDUP_WF_PREP_20260621_233409\\real_exit_tier_b_dedup.csv")

def load(path):
    rows=[]
    with open(path,newline="",encoding="utf-8") as f:
        for r in csv.DictReader(f):
            try:
                rows.append({
                    "time":r["time"],
                    "open":float(r["open"]),
                    "high":float(r["high"]),
                    "low":float(r["low"]),
                    "close":float(r["close"]),
                    "atr_14":float(r["atr_14"]) if r["atr_14"] else 0,
                    "body_pct":float(r["body_pct"]),
                    "session":r["session"],
                    "volatility_state":r["volatility_state"],
                    "spread_state":r["spread_state"],
                    "trend_21_55":r["trend_21_55"]
                })
            except:
                pass
    return rows

def pass_confirm(row,q):
    if row["spread_state"]!="NORMAL": return False
    if q["confirmation"]=="SESSION_REQUIRED" and row["session"] not in ["LONDON","NY"]: return False
    if q["confirmation"]=="VOLATILITY_REQUIRED" and row["volatility_state"]!="HIGH": return False
    if q["confirmation"]=="MTF_REQUIRED" and row["trend_21_55"]=="NA": return False
    return True

def signal(row,q):
    fam=q["family"]
    if fam in ["VWAP_REVERSION","LIQUIDITY_SWEEP_REVERSAL"]:
        if row["trend_21_55"]=="UP" and row["close"]<row["open"]: return "BUY"
        if row["trend_21_55"]=="DOWN" and row["close"]>row["open"]: return "SELL"
    if fam=="BOLLINGER_MEAN_REVERSION":
        if row["body_pct"]>0.65 and row["close"]<row["open"]: return "BUY"
        if row["body_pct"]>0.65 and row["close"]>row["open"]: return "SELL"
    return None

def run(rows,q):
    trades=[]
    max_hold=8
    exit_model=q["exit_model"]
    if exit_model not in ("TIME_EXIT", "ATR_TARGET", "RR_2_TO_1"):
        raise ValueError("P2297_INVALID_EXIT_MODEL")
    if q.get("family") not in ("VWAP_REVERSION", "LIQUIDITY_SWEEP_REVERSAL", "BOLLINGER_MEAN_REVERSION"):
        raise ValueError("P2297_INVALID_FAMILY")
    if q.get("confirmation") not in ("SESSION_REQUIRED", "VOLATILITY_REQUIRED", "MTF_REQUIRED"):
        raise ValueError("P2297_INVALID_CONFIRMATION")

    for i in range(20,len(rows)-max_hold-2):
        if not pass_confirm(rows[i],q): continue
        action=signal(rows[i],q)
        if not action: continue

        entry=rows[i+1]["open"]
        atr=rows[i]["atr_14"]
        if atr<=0: continue

        stop=entry-(1.5*atr) if action=="BUY" else entry+(1.5*atr)
        target=entry+(2.0*atr) if action=="BUY" else entry-(2.0*atr)

        exit_price=None
        for j in range(i+1,min(i+1+max_hold,len(rows))):
            hi,lo=rows[j]["high"],rows[j]["low"]

            if exit_model=="TIME_EXIT":
                if j==i+max_hold:
                    exit_price=rows[j]["close"]; break
            elif exit_model=="ATR_TARGET":
                if action=="BUY":
                    if lo<=stop: exit_price=stop; break
                    if hi>=target: exit_price=target; break
                else:
                    if hi>=stop: exit_price=stop; break
                    if lo<=target: exit_price=target; break
            elif exit_model=="RR_2_TO_1":
                risk=abs(entry-stop)
                rr=entry+(2*risk) if action=="BUY" else entry-(2*risk)
                if action=="BUY":
                    if lo<=stop: exit_price=stop; break
                    if hi>=rr: exit_price=rr; break
                else:
                    if hi>=stop: exit_price=stop; break
                    if lo<=rr: exit_price=rr; break

        if exit_price is None:
            exit_price=rows[min(i+max_hold,len(rows)-1)]["close"]

        pnl=(exit_price-entry) if action=="BUY" else (entry-exit_price)
        trades.append(pnl)

    if len(trades)<10:
        return {"trades":len(trades),"pf":0,"netprofit":sum(trades)}
    wins=[x for x in trades if x>0]
    losses=[x for x in trades if x<0]
    gw=sum(wins); gl=abs(sum(losses))
    return {"trades":len(trades),"pf":gw/gl if gl and gw else 0,"netprofit":sum(trades)}

def main():
    edges=list(csv.DictReader(open(INPUT,newline="",encoding="utf-8")))
    out=[]
    
    for e in edges:
        rows=load(e["dataset"])
        n=len(rows)
        step=n//4
        parts=[]
        for k in range(4):
            a=k*step
            b=(k+1)*step if k<3 else n
            parts.append(run(rows[a:b],e))
    
        passed=sum(1 for p in parts if p["pf"]>=1.15 and p["netprofit"]>0 and p["trades"]>=10)
        status="FINAL_APPROVED" if passed>=3 else ("FINAL_WATCHLIST" if passed==2 else "FINAL_REJECTED")
    
        out.append({
            "symbol":e["symbol"],
            "timeframe":e["timeframe"],
            "family":e["family"],
            "confirmation":e["confirmation"],
            "exit_model":e["exit_model"],
            "segments_passed":passed,
            "seg1_pf":round(parts[0]["pf"],4),
            "seg2_pf":round(parts[1]["pf"],4),
            "seg3_pf":round(parts[2]["pf"],4),
            "seg4_pf":round(parts[3]["pf"],4),
            "final_status":status,
            "mode":"PAPER_ONLY",
            "real_orders":"FORBIDDEN"
        })
    
    with open(EV/"final_segmented_wf.csv","w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    
    summary={
     "program":"P2297_REAL_EXIT_FINAL_SEGMENT_WF",
     "mode":"PAPER_ONLY",
     "real_orders":"FORBIDDEN",
     "input_edges":len(edges),
     "final_approved":sum(1 for x in out if x["final_status"]=="FINAL_APPROVED"),
     "watchlist":sum(1 for x in out if x["final_status"]=="FINAL_WATCHLIST"),
     "rejected":sum(1 for x in out if x["final_status"]=="FINAL_REJECTED"),
     "status":"FINAL_SEGMENT_WF_COMPLETE",
     "next":"P2298_DECISION"
    }
    (EV/"summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print(json.dumps(summary,indent=2))

if __name__ == "__main__":
    main()
