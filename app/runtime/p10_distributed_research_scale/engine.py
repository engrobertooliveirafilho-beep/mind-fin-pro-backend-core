import json, hashlib
from pathlib import Path
from datetime import datetime, timezone

QUEUES=["ingestion","quality_gate","genome_generation","backtest","walk_forward","monte_carlo","robustness","ranking","reporting"]

def make_job(queue,payload):
    if queue not in QUEUES:
        raise ValueError("unknown queue")
    raw=json.dumps({"queue":queue,"payload":payload},sort_keys=True)
    return {
        "job_id":hashlib.sha256(raw.encode()).hexdigest()[:18],
        "queue":queue,
        "payload":payload,
        "status":"PENDING",
        "live":"FORBIDDEN",
        "real_broker":"DISABLED",
        "promotion_allowed":False,
        "created_at":datetime.now(timezone.utc).isoformat()
    }

def build_plan(datasets=10, genomes=10000):
    if any(type(v) is not int or v<=0 for v in (datasets,genomes)):
        raise ValueError("positive integer counts required")
    jobs=[]
    for i in range(datasets):
        jobs.append(make_job("ingestion",{"dataset_index":i}))
        jobs.append(make_job("quality_gate",{"dataset_index":i}))
    for i in range(0,genomes,1000):
        jobs.append(make_job("genome_generation",{"batch_start":i,"batch_size":min(1000,genomes-i)}))
        jobs.append(make_job("backtest",{"batch_start":i,"batch_size":min(1000,genomes-i)}))
        jobs.append(make_job("walk_forward",{"batch_start":i,"batch_size":min(1000,genomes-i)}))
        jobs.append(make_job("monte_carlo",{"batch_start":i,"batch_size":min(1000,genomes-i)}))
        jobs.append(make_job("robustness",{"batch_start":i,"batch_size":min(1000,genomes-i)}))
    jobs.append(make_job("ranking",{"scope":"unverified_research_only"}))
    jobs.append(make_job("reporting",{"scope":"full_research_audit"}))
    return jobs

def run():
    out=Path("reports/P10.1_DISTRIBUTED_RESEARCH_SCALE")
    out.mkdir(parents=True,exist_ok=True)
    jobs=build_plan()
    manifest={
        "STATUS":"P10.1_PLAN_ONLY",
        "JOBS_EXECUTED":0,
        "QUEUES":QUEUES,
        "JOBS":len(jobs),
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "PROMOTION_ALLOWED":False,
        "EDGE":"NOT_PROVEN",
        "CAUSALITY":"NOT_PROVEN",
        "EXPORT_READY":True
    }
    (out/"P10.1_jobs.json").write_text(json.dumps(jobs,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P10.1_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    return manifest

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
