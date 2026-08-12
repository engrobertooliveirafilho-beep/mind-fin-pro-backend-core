import json
from pathlib import Path
from datetime import datetime, UTC

def clamp(x,a=0,b=1):
    return max(a,min(b,float(x)))

def uncertainty_score(validation_report):
    oos=validation_report.get("out_of_sample",{})
    mc=validation_report.get("monte_carlo",{})
    deg=validation_report.get("degradation",{})
    stress=validation_report.get("cost_stress",{})

    trades=float(oos.get("trades",0))
    pf=float(oos.get("profit_factor",0))
    expectancy=float(oos.get("expectancy",0))
    dd=float(oos.get("max_drawdown",0))

    sample_conf=clamp(trades/50)
    pf_conf=clamp((pf-1)/1.5)
    exp_conf=clamp(expectancy/2)
    dd_penalty=clamp(dd/50)

    robustness=(0.25*(1 if mc.get("passed") else 0)+0.25*(1 if deg.get("passed") else 0)+0.25*(1 if stress.get("passed") else 0)+0.25*sample_conf)
    confidence=clamp((sample_conf+pf_conf+exp_conf+robustness)/4 - dd_penalty*0.25)
    uncertainty=clamp(1-confidence)

    if confidence>=0.75 and robustness>=0.70:
        decision="UNCERTAINTY_ACCEPT_RESEARCH"
    elif confidence>=0.45:
        decision="UNCERTAINTY_RETEST"
    else:
        decision="UNCERTAINTY_BLOCK"

    return {
        "confidence":confidence,
        "uncertainty":uncertainty,
        "robustness":robustness,
        "decision":decision,
        "production":"BLOCKED",
        "edge_claim":"NONE"
    }

def uncertainty_authority(genome_id, validation_report):
    r=uncertainty_score(validation_report)
    report={
        "authority":"P8.78_UNCERTAINTY_AUTHORITY",
        "created_at":datetime.now(UTC).isoformat(),
        "genome_id":genome_id,
        "uncertainty":r,
        "paper_candidate_allowed":r["decision"]=="UNCERTAINTY_ACCEPT_RESEARCH",
        "production":"BLOCKED",
        "live":"FORBIDDEN",
        "edge_claim":"NONE"
    }
    Path("mind_trader/reports").mkdir(parents=True,exist_ok=True)
    Path("mind_trader/reports/P8.78_uncertainty_authority.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    return report
