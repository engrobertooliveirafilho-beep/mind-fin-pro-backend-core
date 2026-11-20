import math
from .execution import simulate_fill

def replay_portfolio(name, edges, candles, features, risk_pct=0.01, initial_capital=100.0, spread_r=0.03, slippage_r=0.02, commission_r=0.01, max_trades_per_day=20):
    for value, positive in ((risk_pct,False),(initial_capital,True),(spread_r,False),(slippage_r,False),(commission_r,False)):
        if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value<0 or (positive and value==0):
            raise ValueError("UNSAFE_PAPER_PARAMETER")
    if risk_pct>1 or not isinstance(max_trades_per_day,int) or isinstance(max_trades_per_day,bool) or max_trades_per_day<1:
        raise ValueError("UNSAFE_PAPER_PARAMETER")
    if not isinstance(edges,list) or not isinstance(candles,list) or not isinstance(features,dict):
        raise ValueError("INVALID_INPUT")
    if any(not isinstance(e,dict) or not isinstance(e.get("edge_id"),str) or not e["edge_id"] for e in edges):
        raise ValueError("INVALID_EDGE")
    ids=[e["edge_id"] for e in edges]
    if len(set(ids))!=len(ids): raise ValueError("DUPLICATE_EDGE_ID")
    capital=initial_capital
    peak=capital
    max_dd=0.0
    trades=[]
    curve=[]
    daily_count={}
    cooldown={e["edge_id"]:0 for e in edges}
    pending=[]
    occupied=set()

    for i in range(60,len(candles)):
        for fill in sorted((f for f in pending if f["exit_i"]==i),key=lambda f:f["edge_id"]):
            before=capital
            pnl=fill["reserved_risk"]*fill["r"]
            capital=max(0.01,capital+pnl)
            peak=max(peak,capital)
            dd=(peak-capital)/peak*100
            max_dd=max(max_dd,dd)
            fill.update({"portfolio":name,"capital_before":round(before,6),
                         "capital_after":round(capital,6),"pnl_usd":round(pnl,6),"dd_pct":round(dd,6)})
            trades.append(fill)
            occupied.remove(fill["edge_id"])
            if fill["r"]<0 and fill.get("risk_model") in ("LOSS_GUARD","COOLDOWN"):
                cooldown[fill["edge_id"]]=3
        pending=[f for f in pending if f["exit_i"]>i]
        day=candles[i]["time"].date().isoformat()
        daily_count.setdefault(day,0)
        active=[]
        for e in edges:
            if daily_count[day]>=max_trades_per_day:
                break
            eid=e["edge_id"]
            if eid in occupied: continue
            if cooldown[eid]>0:
                cooldown[eid]-=1
                continue
            if i>=len(candles)-20: continue
            fill=simulate_fill(e,candles,features,i,spread_r,slippage_r,commission_r)
            if not fill or not isinstance(fill.get("r"),(int,float)) or not math.isfinite(fill["r"]) or fill.get("real_execution_allowed") is not False:
                continue
            fill["edge_id"]=eid
            fill["family"]=e.get("family")
            fill["direction"]=e.get("direction")
            fill["risk_model"]=e.get("risk_model")
            fill["reserved_risk"]=capital*risk_pct
            pending.append(fill)
            occupied.add(eid)
            daily_count[day]+=1
            if fill["r"]<0 and e.get("risk_model") in ["LOSS_GUARD","COOLDOWN"]:
                cooldown[eid]=3

        curve.append({
            "bar":i,
            "time":candles[i]["time"].strftime("%Y-%m-%d %H:%M:%S"),
            "portfolio":name,
            "capital":round(capital,6),
            "dd_pct":round((peak-capital)/peak*100,6)
        })

    wins=sum(1 for t in trades if t["r"]>0)
    losses=sum(1 for t in trades if t["r"]<0)
    gw=sum(t["r"] for t in trades if t["r"]>0)
    gl=abs(sum(t["r"] for t in trades if t["r"]<0))
    pf=gw/gl if gl else (None if gw else 0.0)

    return {
        "portfolio":name,
        "edges":len(edges),
        "initial_capital_usd":initial_capital,
        "final_capital_usd":round(capital,6),
        "multiplier":round(capital/initial_capital,6),
        "return_pct":round((capital/initial_capital-1)*100,6),
        "max_dd_pct":round(max_dd,6),
        "trades":len(trades),
        "wins":wins,
        "losses":losses,
        "winrate":round(wins/max(wins+losses,1)*100,6),
        "pf_r":round(pf,6) if pf is not None else None,
        "risk_pct":risk_pct,
        "max_trades_per_day":max_trades_per_day,
        "real_execution_allowed":False,
        "pending_unsettled":len(pending)
    }, curve, trades
