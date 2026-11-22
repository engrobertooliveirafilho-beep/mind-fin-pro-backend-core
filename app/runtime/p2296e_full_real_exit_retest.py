from pathlib import Path
import csv,json

ROOT=Path(r"C:\Users\MindFin\Desktop\mind-fin-pro-backend-core")
FEATURES=ROOT/"mind_trader/data/features_mt5"
EV=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core\\_evidence\\P2296E_FULL_STRUCTURAL_REAL_EXIT_RETEST_20260621_233208")
QUEUE=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core\\_evidence\\P2292_STRUCTURAL_STRATEGY_ENGINE_20260621_231504\\structural_strategy_queue.csv")

def ds(symbol,timeframe):
    p=FEATURES/f"MT5_{symbol}_{timeframe}_features.csv"
    return p if p.exists() else None

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
                    "trend_9_21":r["trend_9_21"],
                    "trend_21_55":r["trend_21_55"],
                    "trend_55_200":r["trend_55_200"]
                })
            except:
                pass
    return rows

def pass_confirm(row,q):
    if row["spread_state"]!="NORMAL":
        return False
    if q["confirmation"]=="SESSION_REQUIRED" and row["session"] not in ["LONDON","NY"]:
        return False
    if q["confirmation"]=="VOLATILITY_REQUIRED" and row["volatility_state"]!="HIGH":
        return False
    if q["confirmation"]=="MTF_REQUIRED" and row["trend_21_55"]=="NA":
        return False
    return True

def sig(row,prev,q):
    fam=q["family"]

    if fam=="BOLLINGER_MEAN_REVERSION":
        if row["body_pct"]>0.65 and row["close"]<row["open"]:
            return "BUY"
        if row["body_pct"]>0.65 and row["close"]>row["open"]:
            return "SELL"

    if fam=="ATR_VOLATILITY_BREAKOUT":
        if row["volatility_state"]=="HIGH" and row["close"]>row["open"]:
            return "BUY"
        if row["volatility_state"]=="HIGH" and row["close"]<row["open"]:
            return "SELL"

    if fam in ["DONCHIAN_BREAKOUT","PREVIOUS_HIGH_LOW_BREAKOUT","OPENING_RANGE_BREAKOUT"]:
        if row["close"]>prev["high"]:
            return "BUY"
        if row["close"]<prev["low"]:
            return "SELL"

    if fam in ["MTF_ALIGNED_PULLBACK","VWAP_TREND_CONTINUATION","TIME_EXIT_TREND_FOLLOW"]:
        if row["trend_21_55"]=="UP" and row["close"]>row["open"]:
            return "BUY"
        if row["trend_21_55"]=="DOWN" and row["close"]<row["open"]:
            return "SELL"

    if fam in ["VWAP_REVERSION","LIQUIDITY_SWEEP_REVERSAL"]:
        if row["trend_21_55"]=="UP" and row["close"]<row["open"]:
            return "BUY"
        if row["trend_21_55"]=="DOWN" and row["close"]>row["open"]:
            return "SELL"

    return None

def simulate(rows,q):
    trades=[]
    max_hold=8
    exit_model=q["exit_model"]
    if exit_model not in ("TIME_EXIT", "ATR_TARGET", "RR_2_TO_1"):
        raise ValueError("P2296E_INVALID_EXIT_MODEL")

    for i in range(20,len(rows)-max_hold-2):
        row=rows[i]
        if not pass_confirm(row,q):
            continue

        action=sig(row,rows[i-1],q)
        if not action:
            continue

        entry=rows[i+1]["open"]
        atr=row["atr_14"]
        if atr<=0:
            continue

        if action=="BUY":
            stop=entry-(1.5*atr)
            target=entry+(2.0*atr)
        else:
            stop=entry+(1.5*atr)
            target=entry-(2.0*atr)

        exit_price=None
        exit_reason=None
        exit_i=None

        for j in range(i+1,min(i+1+max_hold,len(rows))):
            hi=rows[j]["high"]
            lo=rows[j]["low"]

            if exit_model=="TIME_EXIT":
                if j==i+max_hold:
                    exit_price=rows[j]["close"]
                    exit_reason="TIME_EXIT"
                    exit_i=j
                    break

            elif exit_model=="ATR_TARGET":
                if action=="BUY":
                    if lo<=stop:
                        exit_price=stop; exit_reason="ATR_STOP"; exit_i=j; break
                    if hi>=target:
                        exit_price=target; exit_reason="ATR_TARGET"; exit_i=j; break
                else:
                    if hi>=stop:
                        exit_price=stop; exit_reason="ATR_STOP"; exit_i=j; break
                    if lo<=target:
                        exit_price=target; exit_reason="ATR_TARGET"; exit_i=j; break

            elif exit_model=="RR_2_TO_1":
                risk=abs(entry-stop)
                rr_target=entry+(2*risk) if action=="BUY" else entry-(2*risk)
                if action=="BUY":
                    if lo<=stop:
                        exit_price=stop; exit_reason="RR_STOP"; exit_i=j; break
                    if hi>=rr_target:
                        exit_price=rr_target; exit_reason="RR_TARGET"; exit_i=j; break
                else:
                    if hi>=stop:
                        exit_price=stop; exit_reason="RR_STOP"; exit_i=j; break
                    if lo<=rr_target:
                        exit_price=rr_target; exit_reason="RR_TARGET"; exit_i=j; break

        if exit_price is None:
            exit_i=min(i+max_hold,len(rows)-1)
            exit_price=rows[exit_i]["close"]
            exit_reason="FORCED_TIME_EXIT"

        pnl=(exit_price-entry) if action=="BUY" else (entry-exit_price)
        trades.append(pnl)

    return trades

def metrics(trades):
    if len(trades)<30:
        return None
    wins=[x for x in trades if x>0]
    losses=[x for x in trades if x<0]
    gw=sum(wins)
    gl=abs(sum(losses))
    pf=gw/gl if gl else 999
    wr=len(wins)/len(trades)*100
    payoff=(sum(wins)/len(wins))/(abs(sum(losses)/len(losses))) if wins and losses else 0
    return {
        "trades":len(trades),
        "pf":round(pf,4),
        "winrate":round(wr,2),
        "payoff":round(payoff,4),
        "netprofit":round(sum(trades),6)
    }


def main():
    queue=list(csv.DictReader(open(QUEUE,newline="",encoding="utf-8")))
    cache={}
    results=[]
    blocked=0
    
    for q in queue:
        p=ds(q["symbol"],q["timeframe"])
        if not p:
            blocked+=1
            continue
    
        key=str(p)
        if key not in cache:
            cache[key]=load(p)
    
        trades=simulate(cache[key],q)
        m=metrics(trades)
    
        if not m:
            blocked+=1
            continue
    
        tier="A" if m["pf"]>=1.8 and m["trades"]>=80 and m["payoff"]>=1.3 else ("B" if m["pf"]>=1.45 and m["trades"]>=60 and m["payoff"]>=1.2 else ("C" if m["pf"]>=1.2 else "D"))
    
        results.append({**q,**m,"tier":tier,"dataset":key})
    
    results.sort(key=lambda x:(x["tier"],-x["pf"],-x["trades"]))
    
    with open(EV/"real_exit_structural_results.csv","w",newline="",encoding="utf-8") as f:
        if results:
            w=csv.DictWriter(f,fieldnames=list(results[0].keys()))
            w.writeheader()
            w.writerows(results)
    
    summary={
        "program":"P2296E_FULL_STRUCTURAL_REAL_EXIT_RETEST",
        "mode":"PAPER_ONLY",
        "real_orders":"FORBIDDEN",
        "queued":len(queue),
        "valid_results":len(results),
        "blocked":blocked,
        "tier_A":sum(1 for x in results if x["tier"]=="A"),
        "tier_B":sum(1 for x in results if x["tier"]=="B"),
        "tier_C":sum(1 for x in results if x["tier"]=="C"),
        "tier_D":sum(1 for x in results if x["tier"]=="D"),
        "top_10":results[:10],
        "next":"P2296F_REAL_EXIT_WALK_FORWARD"
    }
    (EV/"summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print(json.dumps(summary,indent=2))

if __name__ == "__main__":
    main()
