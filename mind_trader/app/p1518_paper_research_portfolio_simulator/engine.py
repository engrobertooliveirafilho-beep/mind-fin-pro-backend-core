import json, itertools, math, statistics
from pathlib import Path
from datetime import datetime, UTC

INPUT=Path("reports/P15.17_EDGE_VALIDATION_MEGA_PACK/approved_edges.json")
OUT=Path("reports/P15.18_PAPER_RESEARCH_PORTFOLIO_SIMULATOR")

ALLOCATIONS=[
    {"name":"equal_33","weights":[0.3333,0.3333,0.3334]},
    {"name":"csan3_heavy","weights":[0.50,0.25,0.25]},
    {"name":"ifix_heavy","weights":[0.25,0.50,0.25]},
    {"name":"shul4_heavy","weights":[0.25,0.25,0.50]},
]

def load_edges():
    return json.loads(INPUT.read_text(encoding="utf-8")) if INPUT.exists() else []

def edge_metrics(e):
    ret=float(e.get("total_return",0))
    pf=float(e.get("profit_factor",0))
    trades=int(e.get("trades",0))
    wr=float(e.get("winrate",0))/100
    expectancy=ret/max(trades,1)
    sharpe=(ret/(abs(expectancy)*math.sqrt(trades))) if trades and expectancy else 0
    max_dd=abs(ret)*0.35 if pf>=2 else abs(ret)*0.50
    recovery=ret/max_dd if max_dd else 0
    payoff=(pf*(1-wr)/wr) if wr>0 else 0
    return {
        "edge_id":f'{e.get("symbol")}_{e.get("timeframe")}_{e.get("strategy")}_{e.get("fast")}_{e.get("slow")}',
        "symbol":e.get("symbol"),
        "timeframe":e.get("timeframe"),
        "strategy":e.get("strategy"),
        "fast":e.get("fast"),
        "slow":e.get("slow"),
        "regime":e.get("regime"),
        "profit_factor":pf,
        "trades":trades,
        "winrate":round(wr*100,2),
        "return":round(ret,6),
        "expectancy":round(expectancy,6),
        "payoff_proxy":round(payoff,6),
        "sharpe_proxy":round(sharpe,6),
        "max_drawdown_proxy":round(max_dd,6),
        "recovery_factor_proxy":round(recovery,6),
        "validation_score":e.get("validation_score",0),
        "live":"FORBIDDEN",
        "real_orders":"FORBIDDEN"
    }

def proxy_corr(a,b):
    score=0.0
    if a["timeframe"]==b["timeframe"]: score+=0.35
    if a["strategy"]==b["strategy"]: score+=0.35
    if a["regime"]==b["regime"]: score+=0.20
    if a["symbol"]==b["symbol"]: score+=0.10
    return round(min(score,1.0),4)

def portfolio_metrics(edges, weights):
    ret=sum(e["return"]*w for e,w in zip(edges,weights))
    pf=sum(e["profit_factor"]*w for e,w in zip(edges,weights))
    trades=sum(e["trades"] for e in edges)
    wr=sum(e["winrate"]*w for e,w in zip(edges,weights))
    dd=sum(e["max_drawdown_proxy"]*w for e,w in zip(edges,weights))
    recovery=ret/dd if dd else 0
    sharpe=sum(e["sharpe_proxy"]*w for e,w in zip(edges,weights))
    avg_corr=0
    pairs=list(itertools.combinations(edges,2))
    if pairs:
        avg_corr=sum(proxy_corr(a,b) for a,b in pairs)/len(pairs)
    corr_penalty=0.75 if avg_corr>=0.8 else (0.9 if avg_corr>=0.6 else 1.0)
    institutional_score=(pf*2)+(recovery*1.5)+sharpe-(avg_corr*2)
    approved=pf>=1.50 and recovery>=1.0 and corr_penalty>=0.75
    return {
        "return":round(ret,6),
        "profit_factor":round(pf,6),
        "trades":trades,
        "winrate":round(wr,4),
        "max_drawdown_proxy":round(dd,6),
        "recovery_factor_proxy":round(recovery,6),
        "sharpe_proxy":round(sharpe,6),
        "avg_correlation_proxy":round(avg_corr,6),
        "correlation_penalty":corr_penalty,
        "institutional_score":round(institutional_score,6),
        "portfolio_approved":approved,
        "live":"FORBIDDEN",
        "real_orders":"FORBIDDEN"
    }

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    raw=load_edges()
    singles=[edge_metrics(e) for e in raw]

    corr=[]
    for a,b in itertools.combinations(singles,2):
        corr.append({
            "a":a["edge_id"],
            "b":b["edge_id"],
            "correlation_proxy":proxy_corr(a,b)
        })

    portfolios=[]
    if len(singles)>=3:
        for alloc in ALLOCATIONS:
            m=portfolio_metrics(singles[:3],alloc["weights"])
            portfolios.append({
                "allocation":alloc["name"],
                "weights":alloc["weights"],
                "edges":[e["edge_id"] for e in singles[:3]],
                **m
            })

    portfolios.sort(key=lambda x:x["institutional_score"],reverse=True)
    best=portfolios[0] if portfolios else {}

    report={
        "STATUS":"P15.18_PAPER_RESEARCH_PORTFOLIO_SIMULATOR_IMPLEMENTED",
        "INPUT_EDGES":len(raw),
        "SINGLE_EDGES":len(singles),
        "PORTFOLIOS_TESTED":len(portfolios),
        "BEST_PORTFOLIO":best,
        "LIMITATION":"NO_TRADE_LEVEL_EQUITY_CURVE_AVAILABLE_CORRELATION_IS_PROXY",
        "EDGE":"PAPER_PORTFOLIO_CANDIDATE_FOUND" if best.get("portfolio_approved") else "NOT_PROVEN",
        "CAUSALITY":"NOT_PROVEN",
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "REAL_ORDERS":"FORBIDDEN",
        "NEXT":"P15.19_TRADE_LEVEL_EQUITY_CURVE_RECONSTRUCTION",
        "EXPORT_READY":True,
        "generated_at":datetime.now(UTC).isoformat()
    }

    (OUT/"single_edge_results.json").write_text(json.dumps(singles,indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"correlation_matrix.json").write_text(json.dumps(corr,indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"portfolio_results.json").write_text(json.dumps(portfolios,indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"best_portfolio.json").write_text(json.dumps(best,indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"institutional_snapshot.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    return report

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
