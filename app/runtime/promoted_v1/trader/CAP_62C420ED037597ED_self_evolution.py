import json
from pathlib import Path
from datetime import datetime, UTC

def score_validation(report):
    cls=report.get("classification","")
    oos=report.get("out_of_sample",{})
    mc=report.get("monte_carlo",{})
    deg=report.get("degradation",{})
    stress=report.get("cost_stress",{})
    score=0
    if cls=="PAPER_TRADING_CANDIDATE": score+=100
    if cls=="RESEARCH_CANDIDATE": score+=40
    score += float(oos.get("expectancy",0))*20
    score += min(float(oos.get("profit_factor",0)),5)*10
    score -= float(oos.get("max_drawdown",0))*0.5
    score += 10 if mc.get("passed") else -20
    score += 10 if deg.get("passed") else -20
    score += 10 if stress.get("passed") else -20
    return score

def detect_deterioration(history):
    if len(history)<3:
        return {"deteriorated":False,"reason":"INSUFFICIENT_HISTORY"}
    scores=[float(x["score"]) for x in history]
    if scores[-1] < scores[-2] < scores[-3]:
        return {"deteriorated":True,"reason":"THREE_STEP_SCORE_DECAY"}
    if scores[-1] < max(scores)*0.5:
        return {"deteriorated":True,"reason":"SCORE_COLLAPSE_VS_PEAK"}
    return {"deteriorated":False,"reason":"STABLE"}

def evolve_genome(genome_id, validation_report, prior_history=None):
    prior_history=prior_history or []
    score=score_validation(validation_report)
    history=prior_history+[{"ts":datetime.now(UTC).isoformat(),"score":score}]
    det=detect_deterioration(history)
    cls=validation_report.get("classification","REJECTED_EDGE")
    if det["deteriorated"]:
        status="DEMOTED_RESEARCH_REVIEW"
    elif cls=="PAPER_TRADING_CANDIDATE" and score>80:
        status="PAPER_CANDIDATE_ONLY"
    elif cls=="RESEARCH_CANDIDATE" and score>20:
        status="KEEP_RESEARCH"
    else:
        status="REJECT_OR_RETEST"
    return {
        "genome_id":genome_id,
        "score":score,
        "history":history,
        "deterioration":det,
        "status":status,
        "production":"BLOCKED",
        "edge_claim":"NONE"
    }

def evolve_portfolio(validation_reports, prior_histories=None):
    prior_histories=prior_histories or {}
    evolved=[evolve_genome(gid,rep,prior_histories.get(gid,[])) for gid,rep in validation_reports.items()]
    ranked=sorted(evolved,key=lambda x:x["score"],reverse=True)
    return {
        "evaluated":len(ranked),
        "ranked":ranked,
        "paper_candidates":sum(1 for x in ranked if x["status"]=="PAPER_CANDIDATE_ONLY"),
        "demoted":sum(1 for x in ranked if x["status"]=="DEMOTED_RESEARCH_REVIEW"),
        "decision":"SELF_EVOLUTION_RESEARCH_ONLY",
        "production":"BLOCKED",
        "edge_claim":"NONE"
    }

def save_self_evolution_report(report,path="mind_trader/reports/P8.40_self_evolution.json"):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    return path
