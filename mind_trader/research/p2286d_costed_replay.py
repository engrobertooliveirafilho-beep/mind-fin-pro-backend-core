"""Corrected research-only replay adapter for archived P2286D logic.
Costs are explicit price units, not broker/contract costs. No order APIs.
"""
from __future__ import annotations
import csv, json, math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

REQUIRED=("time","open","close","sma_9","sma_21","sma_55","sma_200","atr_pct","session","volatility_state","spread_state","trend_9_21","trend_21_55","trend_55_200")

@dataclass(frozen=True)
class Trade:
    side:str
    entry_time:str
    exit_time:str
    entry_price:float
    exit_price:float
    gross_pnl:float
    entry_cost:float
    exit_cost:float
    net_pnl:float
    exit_reason:str

def load_feature_rows(path:str|Path)->list[dict]:
    rows=[]
    with Path(path).open("r",newline="",encoding="utf-8-sig") as f:
        reader=csv.DictReader(f)
        missing=sorted(set(REQUIRED)-set(reader.fieldnames or []))
        if missing: raise ValueError("MISSING_COLUMNS:"+",".join(missing))
        previous=None
        for line,raw in enumerate(reader,start=2):
            if not raw.get("time"): raise ValueError(f"MISSING_TIME:{line}")
            row=dict(raw)
            for key in ("open","close","sma_9","sma_21","sma_55","sma_200","atr_pct"):
                value=raw.get(key,"")
                if value in (None,""): row[key]=None
                else:
                    try: number=float(value)
                    except (TypeError,ValueError) as exc: raise ValueError(f"INVALID_NUMBER:{line}:{key}") from exc
                    if not math.isfinite(number): raise ValueError(f"NONFINITE_NUMBER:{line}:{key}")
                    row[key]=number
            if row["open"] is None or row["close"] is None: raise ValueError(f"MISSING_PRICE:{line}")
            if previous is not None and row["time"]<=previous: raise ValueError(f"NON_MONOTONIC_TIME:{line}")
            previous=row["time"]; rows.append(row)
    if len(rows)<3: raise ValueError("INSUFFICIENT_ROWS")
    return rows

def _signal(row:dict,strategy:str,fast:int,session:str,volatility:str,spread:str,trend_filter:str)->str|None:
    if session!="ANY" and row["session"]!=session: return None
    if volatility!="ANY" and row["volatility_state"]!=volatility: return None
    if spread!="ANY" and row["spread_state"]!=spread: return None
    if trend_filter!="ANY" and row.get(trend_filter)!="UP": return None
    fast_ma=row.get(f"sma_{fast}")
    if fast_ma is None: return None
    if strategy=="TREND_PULLBACK":
        if row["trend_21_55"]=="UP" and row["close"]>fast_ma: return "BUY"
        if row["trend_21_55"]=="DOWN" and row["close"]<fast_ma: return "SELL"
    elif strategy=="VOL_BREAKOUT":
        if row["volatility_state"]=="HIGH" and row["close"]>row["open"]: return "BUY"
        if row["volatility_state"]=="HIGH" and row["close"]<row["open"]: return "SELL"
    elif strategy=="SESSION_TREND":
        if row["session"] in ("LONDON","NY"):
            if row["trend_9_21"]=="UP": return "BUY"
            if row["trend_9_21"]=="DOWN": return "SELL"
    else: raise ValueError(f"UNSUPPORTED_STRATEGY:{strategy}")
    return None

def replay(rows:Iterable[dict],*,strategy:str="TREND_PULLBACK",fast:int=9,session_filter:str="ANY",volatility_filter:str="ANY",spread_filter:str="ANY",trend_filter:str="ANY",cost_per_side:float|None=None)->dict:
    if cost_per_side is None or not math.isfinite(float(cost_per_side)) or float(cost_per_side)<0:
        raise ValueError("EXPLICIT_NONNEGATIVE_COST_PER_SIDE_REQUIRED")
    if fast not in (9,21,55,200): raise ValueError("UNSUPPORTED_FAST_MA")
    data=list(rows)
    if len(data)<3: raise ValueError("INSUFFICIENT_ROWS")
    cost=float(cost_per_side); position=None; trades=[]; warmup=0
    def close_position(row,price,reason):
        nonlocal position
        if position is None: return
        gross=(price-position["entry_price"]) if position["side"]=="BUY" else (position["entry_price"]-price)
        trades.append(Trade(position["side"],position["entry_time"],row["time"],position["entry_price"],price,gross,cost,cost,gross-2*cost,reason))
        position=None
    # Signal at bar i close; fill at next bar open.
    for i in range(len(data)-1):
        row=data[i]
        if row.get(f"sma_{fast}") is None: warmup+=1; continue
        sig=_signal(row,strategy,fast,session_filter,volatility_filter,spread_filter,trend_filter)
        if sig is None: continue
        nxt=data[i+1]; px=float(nxt["open"])
        if position is None: position={"side":sig,"entry_time":nxt["time"],"entry_price":px}
        elif sig==position["side"]: continue
        else:
            close_position(nxt,px,"OPPOSITE_SIGNAL")
            position={"side":sig,"entry_time":nxt["time"],"entry_price":px}
    if position is not None: close_position(data[-1],float(data[-1]["close"]),"TERMINAL_CLOSE")
    wins=[t.net_pnl for t in trades if t.net_pnl>0]; losses=[t.net_pnl for t in trades if t.net_pnl<0]
    equity=peak=dd=0.0
    for t in trades:
        equity+=t.net_pnl; peak=max(peak,equity); dd=max(dd,peak-equity)
    gross=sum(t.gross_pnl for t in trades); net=sum(t.net_pnl for t in trades)
    gp=sum(wins); gl=abs(sum(losses))
    return {"mode":"PAPER_RESEARCH_ONLY","real_orders":"FORBIDDEN","strategy":strategy,"fast_ma":fast,
        "cost_per_side_price_units":cost,"rows":len(data),"warmup_rows_skipped":warmup,"trades":len(trades),
        "wins":len(wins),"losses":len(losses),"win_rate_pct":round(len(wins)/len(trades)*100,6) if trades else 0.0,
        "gross_pnl_price_units":round(gross,8),"total_cost_price_units":round(sum(t.entry_cost+t.exit_cost for t in trades),8),
        "net_pnl_price_units":round(net,8),"profit_factor":round(gp/gl,8) if gl else (None if not gp else "INF"),
        "max_drawdown_price_units":round(dd,8),"terminal_position_closed":position is None,
        "trades_ledger":[asdict(t) for t in trades]}

def run_file(path:str|Path,**kwargs)->dict:
    return replay(load_feature_rows(path),**kwargs)

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser(); p.add_argument("dataset"); p.add_argument("--cost-per-side",type=float,required=True)
    p.add_argument("--strategy",default="TREND_PULLBACK"); p.add_argument("--fast",type=int,default=9); p.add_argument("--output",required=True)
    a=p.parse_args(); result=run_file(a.dataset,cost_per_side=a.cost_per_side,strategy=a.strategy,fast=a.fast)
    Path(a.output).write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k!="trades_ledger"},indent=2))
