import json
from pathlib import Path
from datetime import datetime, UTC

INP=Path("reports/P16.23_EDGE_DECAY_REVALIDATION_AUTO_ARCHIVE/p1623_active_edges.json")
OUT=Path("reports/P16.25_PAPER_PORTFOLIO_FROM_ACTIVE_EDGES")
BLOCKS={"LIVE":"FORBIDDEN","REAL_BROKER":"DISABLED","REAL_ORDERS":"FORBIDDEN","FTMO_REAL":"FORBIDDEN","CAUSALITY":"NOT_PROVEN"}

def load(): return json.loads(INP.read_text(encoding="utf-8")) if INP.exists() else []
def edge_score(e): return max(0.01,(float(e.get("profit_factor") or 0)*(1-float(e.get("max_drawdown") or 0))*(1-float(e.get("decay_revalidation_score") or 0))))
def allocate(edges):
    scored=[{**e,"portfolio_score":edge_score(e)} for e in edges]
    total=sum(x["portfolio_score"] for x in scored) or 1
    return [{**x,"paper_weight":round(x["portfolio_score"]/total,6),**BLOCKS} for x in scored]

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    portfolio=allocate(load())
    report={"STATUS":"P16.25_PAPER_PORTFOLIO_CONSTRUCTION_FROM_ACTIVE_EDGES_IMPLEMENTED","PORTFOLIO_EDGES":len(portfolio),"TOTAL_WEIGHT":round(sum(x["paper_weight"] for x in portfolio),6) if portfolio else 0,"NEXT":"P16.26_PAPER_PORTFOLIO_SIMULATION_AND_RISK_HEAT",**BLOCKS,"generated_at":datetime.now(UTC).isoformat()}
    (OUT/"p1625_paper_portfolio.json").write_text(json.dumps(portfolio,indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"p1625_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    return report
if __name__=="__main__": print(json.dumps(run(),indent=2,ensure_ascii=False))
