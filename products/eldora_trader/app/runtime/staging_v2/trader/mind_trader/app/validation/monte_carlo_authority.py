import json, random
from pathlib import Path
from datetime import datetime, UTC

def monte_carlo_authority(trades, runs=500, seed=826, max_dd_allowed=20):
    if len(trades)<20:
        return {"decision":"MONTE_CARLO_INSUFFICIENT_TRADES","passed":False,"production":"BLOCKED","edge_claim":"NONE"}
    pnl=[float(t["pnl"]) for t in trades]
    rnd=random.Random(seed)
    nets=[]; dds=[]
    for _ in range(runs):
        sample=[rnd.choice(pnl) for __ in pnl]
        cur=0; peak=0; dd=0
        for x in sample:
            cur+=x
            peak=max(peak,cur)
            dd=max(dd,peak-cur)
        nets.append(cur); dds.append(dd)
    nets.sort(); dds.sort()
    p05=nets[int(0.05*(runs-1))]
    p50=nets[int(0.50*(runs-1))]
    p95dd=dds[int(0.95*(runs-1))]
    passed=p05>0 and p95dd<=max_dd_allowed
    report={
        "authority":"P8.82_MONTE_CARLO_AUTHORITY",
        "created_at":datetime.now(UTC).isoformat(),
        "runs":runs,
        "trades":len(trades),
        "p05_net_profit":p05,
        "p50_net_profit":p50,
        "p95_drawdown":p95dd,
        "max_dd_allowed":max_dd_allowed,
        "passed":passed,
        "decision":"MONTE_CARLO_PASS_RESEARCH_ONLY" if passed else "MONTE_CARLO_REJECT_OR_RETEST",
        "production":"BLOCKED",
        "live":"FORBIDDEN",
        "edge_claim":"NONE"
    }
    Path("mind_trader/reports").mkdir(parents=True,exist_ok=True)
    Path("mind_trader/reports/P8.82_monte_carlo_authority.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    return report
