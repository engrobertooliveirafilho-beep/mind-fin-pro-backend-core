from dataclasses import dataclass
import pandas as pd

@dataclass(frozen=True)
class CostModel:
    spread_r: float
    commission_r: float
    slippage_r: float
    financing_r: float = 0.0
    @property
    def total_r(self):
        values=(self.spread_r,self.commission_r,self.slippage_r,self.financing_r)
        if any(v < 0 for v in values): raise ValueError("Costs must be non-negative")
        return sum(values)

@dataclass(frozen=True)
class RiskConfig:
    risk_per_trade: float = 0.0025
    max_open_risk: float = 0.02
    initial_equity: float = 10000.0

def validate_events(df):
    required={"edge_id","entry_time","exit_time","pnl_r","holding_bars","mode","real_orders","ftmo_real","real_execution_allowed"}
    missing=required-set(df.columns)
    if missing: raise ValueError(f"Missing columns: {sorted(missing)}")
    if not (df["mode"]=="PAPER_ONLY").all(): raise ValueError("Non-PAPER event")
    if not (df["real_orders"]=="FORBIDDEN").all() or not (df["ftmo_real"]=="FORBIDDEN").all(): raise ValueError("Safety flags violated")
    if df["real_execution_allowed"].astype(bool).any(): raise ValueError("Real execution flag enabled")
    if (df["exit_time"]<=df["entry_time"]).any(): raise ValueError("Invalid event interval")
    if df.duplicated(["edge_id","entry_time","exit_time"]).any(): raise ValueError("Duplicate event")
    return True

def replay(df, costs: CostModel, risk: RiskConfig):
    validate_events(df)
    if not 0 < risk.risk_per_trade <= risk.max_open_risk <= 1: raise ValueError("Invalid risk limits")
    timeline={}
    for idx,row in df.iterrows():
        timeline.setdefault(row.entry_time,{"entries":[],"exits":[]})["entries"].append((idx,row))
        timeline.setdefault(row.exit_time,{"entries":[],"exits":[]})["exits"].append((idx,row))
    equity=peak=risk.initial_equity; maxdd=0.0; active={}; ledger=[]; rejected=0
    for ts in sorted(timeline):
        batch=timeline[ts]
        for idx,row in batch["exits"]:
            if idx in active:
                risk_cash=active.pop(idx); net_r=float(row.pnl_r)-costs.total_r
                pnl=risk_cash*net_r; equity+=pnl; peak=max(peak,equity)
                maxdd=max(maxdd,(peak-equity)/peak if peak else 0.0)
                ledger.append({"edge_id":row.edge_id,"entry_time":row.entry_time,"exit_time":row.exit_time,"gross_r":float(row.pnl_r),"net_r":net_r,"risk_cash":risk_cash,"pnl_cash":pnl,"equity_after":equity})
        entrants=batch["entries"]
        if entrants:
            capacity=max(0.0,equity*risk.max_open_risk-sum(active.values()))
            desired=equity*risk.risk_per_trade*len(entrants)
            scale=min(1.0,capacity/desired) if desired else 0.0
            for idx,row in entrants:
                cash=equity*risk.risk_per_trade*scale
                if cash>0: active[idx]=cash
                else: rejected+=1
    return {"equity_end":equity,"max_dd_pct":maxdd*100,"unclosed_positions":len(active),"closed_events":len(ledger),"rejected_entries":rejected},pd.DataFrame(ledger)
