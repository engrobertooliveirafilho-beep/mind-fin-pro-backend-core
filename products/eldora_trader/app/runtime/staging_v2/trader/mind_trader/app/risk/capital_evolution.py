import json, math
from pathlib import Path

def fixed_fractional_risk(equity, risk_pct=0.005, min_risk=1.0, max_risk=1000.0):
    if equity <= 0:
        return {"risk_amount":0,"decision":"BLOCK_NO_EQUITY"}
    risk=max(min_risk,min(equity*risk_pct,max_risk))
    return {"risk_amount":risk,"risk_pct":risk_pct,"decision":"RISK_OK"}

def position_size(entry, stop, risk_amount, point_value=1.0, max_size=999999):
    dist=abs(float(entry)-float(stop)) if stop is not None else 0
    if dist <= 0 or risk_amount <= 0:
        return {"size":0,"decision":"BLOCK_INVALID_STOP_OR_RISK"}
    size=risk_amount/(dist*point_value)
    size=max(0,min(size,max_size))
    return {"size":size,"stop_distance":dist,"decision":"SIZE_OK"}

def drawdown_adjusted_risk(equity, peak_equity, base_risk_pct=0.005):
    if peak_equity <= 0 or equity <= 0:
        return {"risk_pct":0,"drawdown":1,"decision":"BLOCK_INVALID_EQUITY"}
    dd=(peak_equity-equity)/peak_equity
    if dd >= 0.10:
        return {"risk_pct":0,"drawdown":dd,"decision":"KILL_SWITCH_DRAWDOWN"}
    if dd >= 0.06:
        return {"risk_pct":base_risk_pct*0.25,"drawdown":dd,"decision":"SEVERE_RISK_REDUCTION"}
    if dd >= 0.03:
        return {"risk_pct":base_risk_pct*0.5,"drawdown":dd,"decision":"RISK_REDUCTION"}
    return {"risk_pct":base_risk_pct,"drawdown":dd,"decision":"NORMAL_RISK"}

def approximate_risk_of_ruin(win_rate, payoff, risk_pct, max_loss_pct=0.10):
    if win_rate <= 0 or payoff <= 0 or risk_pct <= 0:
        return {"risk_of_ruin":1.0,"decision":"RUIN_HIGH"}
    edge=win_rate*payoff-(1-win_rate)
    if edge <= 0:
        return {"risk_of_ruin":1.0,"decision":"RUIN_HIGH"}
    loss_units=max_loss_pct/risk_pct
    r=math.exp(-2*edge*loss_units/(payoff+1))
    r=max(0,min(1,r))
    return {"risk_of_ruin":r,"decision":"RUIN_ACCEPTABLE" if r<0.05 else "RUIN_TOO_HIGH"}

def capital_plan(equity, peak_equity, entry, stop, win_rate, payoff, ftmo_daily_remaining=5000, ftmo_total_remaining=10000, point_value=1.0):
    adj=drawdown_adjusted_risk(equity,peak_equity)
    if adj["risk_pct"] <= 0:
        return {"decision":"BLOCK_TRADE","reason":adj["decision"],"production":"BLOCKED","edge_claim":"NONE"}
    risk=fixed_fractional_risk(equity,adj["risk_pct"])
    risk_amount=min(risk["risk_amount"],ftmo_daily_remaining*0.5,ftmo_total_remaining*0.25)
    ruin=approximate_risk_of_ruin(win_rate,payoff,adj["risk_pct"])
    size=position_size(entry,stop,risk_amount,point_value)
    if ruin["decision"]!="RUIN_ACCEPTABLE":
        return {"decision":"BLOCK_TRADE","reason":"RISK_OF_RUIN_TOO_HIGH","risk":risk,"drawdown":adj,"ruin":ruin,"size":size,"production":"BLOCKED","edge_claim":"NONE"}
    if size["decision"]!="SIZE_OK" or size["size"]<=0:
        return {"decision":"BLOCK_TRADE","reason":"INVALID_POSITION_SIZE","risk":risk,"drawdown":adj,"ruin":ruin,"size":size,"production":"BLOCKED","edge_claim":"NONE"}
    return {"decision":"ALLOW_SIMULATED_SIZE","risk_amount":risk_amount,"drawdown":adj,"ruin":ruin,"size":size,"production":"BLOCKED","edge_claim":"NONE"}

def save_capital_report(report,path="mind_trader/reports/P8.39_capital_evolution.json"):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    return path
