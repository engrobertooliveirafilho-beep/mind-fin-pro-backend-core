import random, statistics, json
from pathlib import Path

def split_trades(trades, ratio=0.7):
    if len(trades) < 10:
        return [], trades
    cut = int(len(trades) * ratio)
    return trades[:cut], trades[cut:]

def trade_metrics(trades):
    if not trades:
        return {"trades":0,"net_profit":0,"profit_factor":0,"expectancy":0,"win_rate":0,"max_drawdown":0}
    pnl=[float(t["pnl"]) for t in trades]
    wins=[x for x in pnl if x>0]
    losses=[x for x in pnl if x<0]
    equity=[]; cur=0; peak=0; dd=0
    for x in pnl:
        cur+=x; peak=max(peak,cur); dd=max(dd,peak-cur); equity.append(cur)
    pf=(sum(wins)/abs(sum(losses))) if losses else (999 if wins else 0)
    return {"trades":len(trades),"net_profit":sum(pnl),"profit_factor":pf,"expectancy":statistics.mean(pnl),"win_rate":len(wins)/len(pnl),"max_drawdown":dd}

def monte_carlo(trades, runs=300, seed=826):
    if not trades:
        return {"runs":runs,"p05_net_profit":0,"p50_net_profit":0,"p95_drawdown":0,"passed":False}
    rnd=random.Random(seed)
    nets=[]; dds=[]
    pnl=[float(t["pnl"]) for t in trades]
    for _ in range(runs):
        sample=[rnd.choice(pnl) for __ in pnl]
        cur=0; peak=0; dd=0
        for x in sample:
            cur+=x; peak=max(peak,cur); dd=max(dd,peak-cur)
        nets.append(cur); dds.append(dd)
    nets.sort(); dds.sort()
    p05=nets[int(0.05*(len(nets)-1))]
    p50=nets[int(0.50*(len(nets)-1))]
    p95dd=dds[int(0.95*(len(dds)-1))]
    return {"runs":runs,"p05_net_profit":p05,"p50_net_profit":p50,"p95_drawdown":p95dd,"passed":p05>0}

def degradation_test(trades, haircut=0.30):
    degraded=[{"pnl": float(t["pnl"])*(1-haircut) if float(t["pnl"])>0 else float(t["pnl"])*(1+haircut)} for t in trades]
    m=trade_metrics(degraded)
    return {"haircut":haircut,"metrics":m,"passed":m["net_profit"]>0 and m["profit_factor"]>1.1}

def cost_stress_test(trades, extra_cost=1.0):
    stressed=[{"pnl": float(t["pnl"])-extra_cost} for t in trades]
    m=trade_metrics(stressed)
    return {"extra_cost":extra_cost,"metrics":m,"passed":m["net_profit"]>0 and m["profit_factor"]>1.1}

def classify_edge(ins, oos, mc, deg, stress):
    hard = [
        ins["trades"] >= 10,
        oos["trades"] >= 3,
        ins["profit_factor"] > 1.1,
        oos["profit_factor"] > 1.1,
        ins["expectancy"] > 0,
        oos["expectancy"] > 0,
        mc["passed"],
        deg["passed"],
        stress["passed"]
    ]
    if all(hard):
        return "PAPER_TRADING_CANDIDATE"
    if ins["expectancy"] > 0 and ins["profit_factor"] > 1.05:
        return "RESEARCH_CANDIDATE"
    return "REJECTED_EDGE"

def validate_backtest_trades(trades):
    ins_trades,oos_trades=split_trades(trades)
    ins=trade_metrics(ins_trades)
    oos=trade_metrics(oos_trades)
    mc=monte_carlo(trades)
    deg=degradation_test(trades)
    stress=cost_stress_test(trades)
    classification=classify_edge(ins,oos,mc,deg,stress)
    return {
        "in_sample":ins,
        "out_of_sample":oos,
        "monte_carlo":mc,
        "degradation":deg,
        "cost_stress":stress,
        "classification":classification,
        "production":"BLOCKED",
        "edge_claim":"NONE_UNTIL_PAPER_AND_LIVE_EVIDENCE"
    }

def save_validation_report(report,path="mind_trader/reports/P8.30_edge_validation_report.json"):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    return path
