from .execution import simulate_fill

def replay_portfolio(name, edges, candles, features, risk_pct=0.01, initial_capital=100.0, spread_r=0.03, slippage_r=0.02, commission_r=0.01, max_trades_per_day=20):
    capital=initial_capital
    peak=capital
    max_dd=0.0
    trades=[]
    curve=[]
    daily_count={}
    cooldown={e["edge_id"]:0 for e in edges}

    for i in range(60,len(candles)-20):
        day=candles[i]["time"].date().isoformat()
        daily_count.setdefault(day,0)
        active=[]
        for e in edges:
            if daily_count[day]>=max_trades_per_day:
                break
            eid=e["edge_id"]
            if cooldown[eid]>0:
                cooldown[eid]-=1
                continue
            fill=simulate_fill(e,candles,features,i,spread_r,slippage_r,commission_r)
            if not fill:
                continue
            fill["edge_id"]=eid
            fill["family"]=e.get("family")
            fill["direction"]=e.get("direction")
            active.append(fill)
            daily_count[day]+=1
            if fill["r"]<0 and e.get("risk_model") in ["LOSS_GUARD","COOLDOWN"]:
                cooldown[eid]=3

        for fill in active:
            before=capital
            pnl=capital*risk_pct*fill["r"]
            capital=max(0.01,capital+pnl)
            peak=max(peak,capital)
            dd=(peak-capital)/peak*100
            max_dd=max(max_dd,dd)
            fill.update({
                "portfolio":name,
                "capital_before":round(before,6),
                "capital_after":round(capital,6),
                "pnl_usd":round(pnl,6),
                "dd_pct":round(dd,6)
            })
            trades.append(fill)

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
    pf=gw/gl if gl else 999.0

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
        "pf_r":round(pf,6),
        "risk_pct":risk_pct,
        "max_trades_per_day":max_trades_per_day,
        "real_execution_allowed":False
    }, curve, trades
