import json, random, statistics
from pathlib import Path
from datetime import datetime, UTC

def parameter_sensitivity(results):
    if not results:
        return {"passed":False,"reason":"NO_RESULTS"}
    vals=[float(x.get("expectancy",0)) for x in results]
    mean=statistics.mean(vals)
    stdev=statistics.stdev(vals) if len(vals)>1 else 0
    stability=1-(stdev/(abs(mean)+1e-9))
    return {"mean_expectancy":mean,"stdev":stdev,"stability":stability,"passed":mean>0 and stability>-1}

def randomization_test(trades, runs=100, seed=826):
    if len(trades)<10:
        return {"passed":False,"reason":"INSUFFICIENT_TRADES"}
    pnl=[float(t["pnl"]) for t in trades]
    real=sum(pnl)
    rnd=random.Random(seed)
    sims=[]
    for _ in range(runs):
        s=pnl[:]
        rnd.shuffle(s)
        sims.append(sum(s[:len(s)//2]))
    p95=sorted(sims)[int(0.95*(len(sims)-1))]
    return {"real_net":real,"random_p95":p95,"passed":real>p95}

def anti_overfitting_authority(genome_id, trades, param_results):
    sens=parameter_sensitivity(param_results)
    rand=randomization_test(trades)
    passed=sens["passed"] and rand["passed"]
    report={
        "authority":"P8.80_ANTI_OVERFITTING_AUTHORITY",
        "created_at":datetime.now(UTC).isoformat(),
        "genome_id":genome_id,
        "parameter_sensitivity":sens,
        "randomization":rand,
        "decision":"ANTI_OVERFITTING_PASS_RESEARCH_ONLY" if passed else "ANTI_OVERFITTING_REJECT_OR_RETEST",
        "production":"BLOCKED",
        "live":"FORBIDDEN",
        "edge_claim":"NONE"
    }
    Path("mind_trader/reports").mkdir(parents=True,exist_ok=True)
    Path("mind_trader/reports/P8.80_anti_overfitting_authority.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    return report
