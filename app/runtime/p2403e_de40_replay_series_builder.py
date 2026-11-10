"""P2403E: causal OHLC replay adapter. No synthetic signal generation."""
from dataclasses import dataclass
from datetime import datetime
from math import isfinite

MODE="PAPER_ONLY"
REAL_ORDERS="FORBIDDEN"
FTMO_REAL="FORBIDDEN"

@dataclass(frozen=True)
class ContractSpec:
    symbol: str
    point_size: float
    contract_size: float
    profit_to_account_fx: float
    account_currency: str
    profit_currency: str
    volume_min: float
    volume_max: float
    volume_step: float
    commission_per_lot_per_side: float
    slippage_points_per_side: float=0.0
    conversion_adjustment_rate: float=0.0
    financing_per_lot_per_day: float|None=None
    price_basis: str="BID"
    stop_spread_points: float|None=None

    def validate(self):
        vals=(self.point_size,self.contract_size,self.profit_to_account_fx,self.volume_min,self.volume_max,self.volume_step)
        if any(not isfinite(float(x)) or float(x)<=0 for x in vals):
            raise ValueError("Invalid positive contract specification")
        if self.volume_max<self.volume_min or self.commission_per_lot_per_side<0:
            raise ValueError("Invalid volume/commission specification")
        if self.slippage_points_per_side<0 or not 0<=self.conversion_adjustment_rate<1:
            raise ValueError("Invalid slippage/conversion adjustment")
        if self.price_basis!="BID":
            raise ValueError("Only BID-based MT5 OHLC is supported")
        if self.stop_spread_points is not None and self.stop_spread_points<0:
            raise ValueError("Invalid stop spread assumption")
        if self.account_currency!=self.profit_currency and self.profit_to_account_fx==1.0:
            raise ValueError("Explicit FX conversion rate required when currencies differ")

def _dt(v):
    return datetime.fromisoformat(str(v).replace("Z","+00:00"))

def validate_candles(candles):
    if not candles: raise ValueError("No OHLC candles")
    required={"timestamp","open","high","low","close","spread"}
    last=None; out=[]
    for row in candles:
        if not required<=set(row): raise ValueError(f"Missing OHLC fields: {sorted(required-set(row))}")
        ts=_dt(row["timestamp"])
        o,h,l,c=(float(row[k]) for k in ("open","high","low","close"))
        spread=float(row["spread"])
        if not all(isfinite(x) for x in (o,h,l,c,spread)) or spread<0: raise ValueError("Invalid OHLC/spread")
        if h<max(o,c) or l>min(o,c) or h<l: raise ValueError("Invalid OHLC ordering")
        if last is not None and ts<=last: raise ValueError("Candles must be strictly chronological and unique")
        out.append({**row,"_ts":ts,"open":o,"high":h,"low":l,"close":c,"spread":spread})
        last=ts
    return out

def build_trade_candidates(candles,signals,spec:ContractSpec):
    """Consume real strategy signals; entry is next bar open, never same-bar close."""
    spec.validate(); bars=validate_candles(candles); by_time={b["_ts"]:i for i,b in enumerate(bars)}
    out=[]
    for sig in signals:
        required={"edge_id","signal_time","exit_time","side","stop_price","exit_price"}
        if not required<=set(sig): raise ValueError(f"Signal missing fields: {sorted(required-set(sig))}")
        st,xt=_dt(sig["signal_time"]),_dt(sig["exit_time"])
        if xt<=st or st not in by_time or xt not in by_time: raise ValueError("Signal/exit timestamp not canonical")
        entry_i=by_time[st]+1
        if entry_i>=len(bars) or bars[entry_i]["_ts"]>=xt: raise ValueError("No causal next-bar entry before exit")
        entry_bar,exit_bar=bars[entry_i],bars[by_time[xt]]
        side=str(sig["side"]).upper()
        if side not in {"BUY","SELL"}: raise ValueError("Side must be BUY or SELL")
        entry_bid=entry_bar["open"]; exit_bid=float(sig["exit_price"]); stop=float(sig["stop_price"])
        if not isfinite(exit_bid) or not isfinite(stop) or exit_bid<exit_bar["low"] or exit_bid>exit_bar["high"]:
            raise ValueError("Invalid exit/stop price or exit outside canonical candle")
        if side=="BUY" and not stop<entry_bid: raise ValueError("BUY stop must be below entry")
        if side=="SELL" and not stop>entry_bid: raise ValueError("SELL stop must be above entry")
        entry_spread=entry_bar["spread"]*spec.point_size
        exit_spread=exit_bar["spread"]*spec.point_size
        slip=spec.slippage_points_per_side*spec.point_size
        if side=="BUY":
            entry_fill=entry_bid+entry_spread+slip; exit_fill=exit_bid-slip
            execution_quote=(exit_fill-entry_fill)*spec.contract_size
            risk_quote=(entry_fill-stop+slip)*spec.contract_size
            spread_cost=entry_spread*spec.contract_size*spec.profit_to_account_fx
        else:
            entry_fill=entry_bid-slip; exit_fill=exit_bid+exit_spread+slip
            execution_quote=(entry_fill-exit_fill)*spec.contract_size
            if spec.stop_spread_points is None:
                raise ValueError("Explicit stop_spread_points required for SELL risk sizing")
            stop_ask=stop+spec.stop_spread_points*spec.point_size
            risk_quote=(stop_ask+slip-entry_fill)*spec.contract_size
            spread_cost=exit_spread*spec.contract_size*spec.profit_to_account_fx
        execution_pnl=execution_quote*spec.profit_to_account_fx
        raw_gross=((exit_bid-entry_bid) if side=="BUY" else (entry_bid-exit_bid))*spec.contract_size*spec.profit_to_account_fx
        risk_per_lot=risk_quote*spec.profit_to_account_fx
        slippage_cost=2*slip*spec.contract_size*spec.profit_to_account_fx
        commission=2*spec.commission_per_lot_per_side
        days=max(0.0,(xt-st).total_seconds()/86400.0)
        if xt.date()!=st.date() and spec.financing_per_lot_per_day is None:
            raise ValueError("Financing schedule required for overnight positions")
        financing=days*float(spec.financing_per_lot_per_day or 0.0)
        conversion=abs(execution_pnl)*spec.conversion_adjustment_rate
        net=execution_pnl-commission-financing-conversion
        if not all(isfinite(x) for x in (raw_gross,risk_per_lot,net)) or risk_per_lot<=0:
            raise ValueError("Invalid per-lot PnL/risk")
        out.append({"edge_id":str(sig["edge_id"]),"entry_time":entry_bar["_ts"].isoformat(),
            "exit_time":xt.isoformat(),"side":side,"entry_fill":entry_fill,"exit_fill":exit_fill,
            "risk_per_lot":risk_per_lot,"gross_pnl_per_lot":raw_gross,
            "execution_pnl_after_spread_slippage_per_lot":execution_pnl,
            "spread_cost_per_lot":spread_cost,"slippage_cost_per_lot":slippage_cost,
            "commission_per_lot":commission,"financing_per_lot":financing,
            "conversion_adjustment_per_lot":conversion,"net_pnl_per_lot":net,
            "volume_min":spec.volume_min,"volume_max":spec.volume_max,"volume_step":spec.volume_step,
            "mode":MODE,"real_orders":REAL_ORDERS,"ftmo_real":FTMO_REAL,"real_execution_allowed":False})
    return out

def safety_contract():
    return {"mode":MODE,"real_orders":REAL_ORDERS,"ftmo_real":FTMO_REAL,
            "runtime_allowed":False,"real_execution_allowed":False}
