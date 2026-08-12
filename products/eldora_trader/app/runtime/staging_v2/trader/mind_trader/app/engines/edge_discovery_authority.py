import json
from pathlib import Path
from datetime import datetime, UTC
from mind_trader.app.engines.feature_store_edge_discovery import feature_store_report
from mind_trader.app.engines.uncertainty_authority import uncertainty_score

def hypothesis_to_validation_report(h):
    pf=1.0 + max(0,float(h.get("hit_rate",0))-0.5)*2
    expectancy=float(h.get("avg_forward_return",0))*1000
    trades=int(h.get("sample_size",0))
    passed=expectancy>0 and trades>=30
    return {
        "out_of_sample":{
            "trades":trades,
            "profit_factor":pf,
            "expectancy":expectancy,
            "max_drawdown":max(1,abs(expectancy)*2)
        },
        "monte_carlo":{"passed":passed},
        "degradation":{"passed":passed and expectancy>0.5},
        "cost_stress":{"passed":passed and expectancy>0.5}
    }

def edge_discovery_authority(symbol,timeframe,db_path="mind_trader/data/market.sqlite"):
    fs=feature_store_report(symbol,timeframe,db_path)
    reviewed=[]
    for h in fs.get("hypotheses",[]):
        vr=hypothesis_to_validation_report(h)
        unc=uncertainty_score(vr)
        reviewed.append({
            "hypothesis":h,
            "validation_proxy":vr,
            "uncertainty":unc,
            "classification":"RESEARCH_HYPOTHESIS" if unc["decision"]!="UNCERTAINTY_BLOCK" else "REJECTED_HYPOTHESIS",
            "edge_claim":"NONE",
            "production":"BLOCKED"
        })
    reviewed=sorted(reviewed,key=lambda x:x["uncertainty"]["confidence"],reverse=True)
    report={
        "authority":"P8.79_EDGE_DISCOVERY_AUTHORITY",
        "created_at":datetime.now(UTC).isoformat(),
        "symbol":symbol,
        "timeframe":timeframe,
        "hypotheses_reviewed":len(reviewed),
        "top":reviewed[:10],
        "decision":"EDGE_DISCOVERY_RESEARCH_ONLY",
        "production":"BLOCKED",
        "live":"FORBIDDEN",
        "edge_claim":"NONE"
    }
    Path("mind_trader/reports").mkdir(parents=True,exist_ok=True)
    Path("mind_trader/reports/P8.79_edge_discovery_authority.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    return report
