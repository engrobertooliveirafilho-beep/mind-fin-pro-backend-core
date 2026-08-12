import json, uuid
from pathlib import Path
from datetime import datetime, UTC
from mind_trader.app.backtest.market_core import load_ohlcv, sma, backtest_sma_cross

def write_replay_event(path, event):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    event["event_id"]=str(uuid.uuid4())
    event["logged_at"]=datetime.now(UTC).isoformat()
    with open(path,"a",encoding="utf-8") as f:
        f.write(json.dumps(event,ensure_ascii=False)+"\n")
    return event

def apply_synthetic_shock(rows, shock_index=None, shock_pct=-0.03):
    out=[dict(r) for r in rows]
    if not out: return out
    idx=shock_index if shock_index is not None else len(out)//2
    idx=max(0,min(idx,len(out)-1))
    for k in ["open","high","low","close"]:
        out[idx][k]=float(out[idx][k])*(1+shock_pct)
    out[idx]["synthetic_event"]="EXTREME_SHOCK"
    out[idx]["shock_pct"]=shock_pct
    return out

def replay_sma_execution(rows, fast=9, slow=21, initial_capital=100000, spread=0.0, slippage=0.0, commission=1.0, ledger_path="mind_trader/logs/P8.38_REPLAY_LEDGER.jsonl"):
    if len(rows)<slow+5:
        return {"status":"INSUFFICIENT_DATA","trades":[],"equity":[initial_capital],"production":"BLOCKED","edge_claim":"NONE"}
    closes=[float(r["close"]) for r in rows]
    f=sma(closes,fast); s=sma(closes,slow)
    cash=initial_capital; pos=0; entry=0; trades=[]; equity=[cash]
    for i in range(1,len(rows)):
        if f[i-1] is None or s[i-1] is None: continue
        price=float(rows[i]["close"])
        buy=f[i-1]<=s[i-1] and f[i]>s[i]
        sell=f[i-1]>=s[i-1] and f[i]<s[i]
        if buy and pos==0:
            entry=price + spread/2 + slippage
            cash-=commission
            pos=1
            write_replay_event(ledger_path,{"type":"ENTRY","ts":rows[i]["ts"],"entry":entry,"fast":fast,"slow":slow,"synthetic_event":rows[i].get("synthetic_event")})
        elif sell and pos==1:
            exitp=price - spread/2 - slippage
            pnl=exitp-entry-commission
            cash+=pnl
            t={"entry":entry,"exit":exitp,"pnl":pnl,"ts":rows[i]["ts"],"synthetic_event":rows[i].get("synthetic_event")}
            trades.append(t)
            pos=0
            write_replay_event(ledger_path,{"type":"EXIT",**t})
        equity.append(cash + ((price-entry) if pos else 0))
    return {"status":"REPLAY_DONE","trades":trades,"equity":equity,"final_equity":equity[-1],"production":"BLOCKED","edge_claim":"NONE"}

def compare_replay_vs_backtest(symbol,timeframe,db_path="mind_trader/data/market.sqlite",fast=9,slow=21):
    rows=load_ohlcv(symbol,timeframe,db_path)
    bt=backtest_sma_cross(symbol,timeframe,fast=fast,slow=slow,db_path=db_path)
    rp=replay_sma_execution(rows,fast=fast,slow=slow)
    return {
        "symbol":symbol,
        "timeframe":timeframe,
        "backtest_net_profit":bt["metrics"]["net_profit"],
        "replay_net_profit":rp["final_equity"]-100000 if rp["status"]=="REPLAY_DONE" else 0,
        "backtest_trades":bt["metrics"]["trades"],
        "replay_trades":len(rp["trades"]),
        "decision":"RESEARCH_COMPARISON_ONLY",
        "production":"BLOCKED",
        "edge_claim":"NONE"
    }

def digital_twin_report(symbol,timeframe,db_path="mind_trader/data/market.sqlite",shock_pct=-0.03):
    rows=load_ohlcv(symbol,timeframe,db_path)
    normal=replay_sma_execution(rows,ledger_path="mind_trader/logs/P8.38_REPLAY_NORMAL.jsonl")
    shocked=replay_sma_execution(apply_synthetic_shock(rows,shock_pct=shock_pct),ledger_path="mind_trader/logs/P8.38_REPLAY_SHOCK.jsonl")
    return {
        "symbol":symbol,
        "timeframe":timeframe,
        "normal":normal,
        "shocked":shocked,
        "shock_pct":shock_pct,
        "decision":"DIGITAL_TWIN_REPLAY_ONLY",
        "production":"BLOCKED",
        "edge_claim":"NONE"
    }

def save_digital_twin_report(report,path="mind_trader/reports/P8.38_digital_twin_replay.json"):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    return path
