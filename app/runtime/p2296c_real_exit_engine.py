from pathlib import Path
import csv,json

ROOT=Path(r"C:\Users\MindFin\Desktop\mind-fin-pro-backend-core")
FEATURES=ROOT/"mind_trader/data/features_mt5"
EV=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core\\_evidence\\P2296C_BUILD_REAL_EXIT_BACKTEST_ENGINE_20260621_232932")

dataset=FEATURES/"MT5_GER40_H1_features.csv"

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

def signal(row):
    if row["trend_21_55"]=="UP" and row["body_pct"]>0.65 and row["close"]<row["open"]:
        return "BUY"
    if row["trend_21_55"]=="DOWN" and row["body_pct"]>0.65 and row["close"]>row["open"]:
        return "SELL"
    return None

def simulate(rows,exit_model):
    if exit_model not in ("TIME_EXIT", "ATR_TARGET", "RR_2_TO_1"):
        raise ValueError("P2296C_INVALID_EXIT_MODEL")
    import math
    if not isinstance(rows, (list, tuple)):
        raise ValueError("P2296C_INVALID_ROWS")
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("P2296C_INVALID_ROWS")
        for field in ("open", "high", "low", "close", "atr_14", "body_pct"):
            value = row.get(field)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError("P2296C_INVALID_MARKET_ROW")
        if not (0 < row["low"] <= min(row["open"], row["close"]) <= max(row["open"], row["close"]) <= row["high"]):
            raise ValueError("P2296C_INVALID_OHLC")
        if row["atr_14"] < 0:
            raise ValueError("P2296C_INVALID_ATR")
    trades=[]
    max_hold=8

    for i in range(20,len(rows)-max_hold-2):
        if rows[i]["spread_state"]!="NORMAL":
            continue

        sig=signal(rows[i])
        if not sig:
            continue

        entry=rows[i+1]["open"]
        atr=rows[i]["atr_14"]
        if atr<=0:
            continue

        if sig=="BUY":
            stop=entry-(1.5*atr)
            target=entry+(2.0*atr)
        else:
            stop=entry+(1.5*atr)
            target=entry-(2.0*atr)

        exit_price=None
        exit_reason=None
        exit_i=None

        for j in range(i+1,min(i+max_hold+1,len(rows))):
            hi=rows[j]["high"]
            lo=rows[j]["low"]

            if exit_model=="TIME_EXIT":
                if j==i+max_hold:
                    exit_price=rows[j]["close"]
                    exit_reason="TIME_EXIT"
                    exit_i=j
                    break

            elif exit_model=="ATR_TARGET":
                if sig=="BUY":
                    if lo<=stop:
                        exit_price=stop
                        exit_reason="ATR_STOP"
                        exit_i=j
                        break
                    if hi>=target:
                        exit_price=target
                        exit_reason="ATR_TARGET"
                        exit_i=j
                        break
                else:
                    if hi>=stop:
                        exit_price=stop
                        exit_reason="ATR_STOP"
                        exit_i=j
                        break
                    if lo<=target:
                        exit_price=target
                        exit_reason="ATR_TARGET"
                        exit_i=j
                        break

            elif exit_model=="RR_2_TO_1":
                risk=abs(entry-stop)
                rr_target=entry+(2*risk) if sig=="BUY" else entry-(2*risk)
                if sig=="BUY":
                    if lo<=stop:
                        exit_price=stop
                        exit_reason="RR_STOP"
                        exit_i=j
                        break
                    if hi>=rr_target:
                        exit_price=rr_target
                        exit_reason="RR_TARGET"
                        exit_i=j
                        break
                else:
                    if hi>=stop:
                        exit_price=stop
                        exit_reason="RR_STOP"
                        exit_i=j
                        break
                    if lo<=rr_target:
                        exit_price=rr_target
                        exit_reason="RR_TARGET"
                        exit_i=j
                        break

        if exit_price is None:
            exit_i=min(i+max_hold,len(rows)-1)
            exit_price=rows[exit_i]["close"]
            exit_reason="FORCED_TIME_EXIT"

        pnl=(exit_price-entry) if sig=="BUY" else (entry-exit_price)

        trades.append({
            "entry_time":rows[i+1]["time"],
            "exit_time":rows[exit_i]["time"],
            "action":sig,
            "entry":entry,
            "exit":exit_price,
            "pnl":pnl,
            "exit_reason":exit_reason,
            "exit_model":exit_model
        })

    return trades

def metrics(trades):
    if not trades:
        return {"trades":0,"pf":0,"winrate":0,"payoff":0,"netprofit":0}
    pnls=[x["pnl"] for x in trades]
    wins=[x for x in pnls if x>0]
    losses=[x for x in pnls if x<0]
    gw=sum(wins)
    gl=abs(sum(losses))
    pf=gw/gl if gl else 999
    wr=len(wins)/len(pnls)*100
    payoff=(sum(wins)/len(wins))/(abs(sum(losses)/len(losses))) if wins and losses else 0
    return {
        "trades":len(pnls),
        "pf":round(pf,4),
        "winrate":round(wr,2),
        "payoff":round(payoff,4),
        "netprofit":round(sum(pnls),6)
    }


def main():
    if not dataset.exists():
        raise SystemExit("DATASET_NOT_FOUND")
    rows=load(dataset)
    all_results=[]
    model_metrics=[]
    
    for model in ["TIME_EXIT","ATR_TARGET","RR_2_TO_1"]:
        trades=simulate(rows,model)
        m=metrics(trades)
        model_metrics.append({"exit_model":model,**m})
        for t in trades:
            all_results.append(t)
    
    with open(EV/"real_exit_trade_ledger.csv","w",newline="",encoding="utf-8") as f:
        if all_results:
            w=csv.DictWriter(f,fieldnames=list(all_results[0].keys()))
            w.writeheader()
            w.writerows(all_results)
    
    with open(EV/"real_exit_model_metrics.csv","w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(model_metrics[0].keys()))
        w.writeheader()
        w.writerows(model_metrics)
    
    unique_metric_sets=len(set((x["trades"],x["pf"],x["winrate"],x["payoff"],x["netprofit"]) for x in model_metrics))
    
    summary={
        "program":"P2296C_BUILD_REAL_EXIT_BACKTEST_ENGINE",
        "mode":"PAPER_ONLY",
        "real_orders":"FORBIDDEN",
        "dataset":str(dataset),
        "exit_models_tested":len(model_metrics),
        "unique_metric_sets":unique_metric_sets,
        "engine_status":"REAL_EXITS_WORKING" if unique_metric_sets>1 else "ENGINE_STILL_SUSPECT",
        "metrics":model_metrics,
        "next":"P2296D_RETEST_STRUCTURAL_QUEUE_WITH_REAL_EXITS"
    }
    
    (EV/"summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print(json.dumps(summary,indent=2))

if __name__ == "__main__":
    main()
