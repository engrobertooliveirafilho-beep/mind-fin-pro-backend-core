import json, hashlib
from pathlib import Path
from datetime import datetime, UTC
from app.p11_data_coverage_engine.engine import build_coverage_matrix

def make_research_job(slot, genome_batch):
    raw=json.dumps({"slot":slot,"genome_batch":genome_batch},sort_keys=True)
    return {
        "job_id":hashlib.sha256(raw.encode()).hexdigest()[:18],
        "symbol":slot["symbol"],
        "asset_class":slot["asset_class"],
        "country":slot["country"],
        "timeframe":slot["timeframe"],
        "genome_batch":genome_batch,
        "status":"BLOCKED_MISSING_CERTIFIED_DATA" if not slot["certified"] else "QUEUED_RESEARCH_BACKTEST",
        "live":"FORBIDDEN",
        "real_broker":"DISABLED",
        "promotion_allowed":False,
        "edge":"NOT_PROVEN",
        "causality":"NOT_PROVEN",
        "created_at":datetime.now(UTC).isoformat()
    }

def build_grid(batch_size=1000, batches=3):
    slots=build_coverage_matrix()
    genome_batches=[{"batch_start":i*batch_size,"batch_size":batch_size} for i in range(batches)]
    jobs=[]
    for slot in slots:
        for batch in genome_batches:
            jobs.append(make_research_job(slot,batch))
    return jobs

def summarize(jobs):
    return {
        "total_jobs":len(jobs),
        "queued":sum(j["status"]=="QUEUED_RESEARCH_BACKTEST" for j in jobs),
        "blocked_missing_certified_data":sum(j["status"]=="BLOCKED_MISSING_CERTIFIED_DATA" for j in jobs)
    }

def run():
    out=Path("reports/P11.5_MULTI_MARKET_RESEARCH_GRID")
    out.mkdir(parents=True,exist_ok=True)
    jobs=build_grid()
    summary=summarize(jobs)
    manifest={
        "STATUS":"P11.5_MULTI_MARKET_RESEARCH_GRID_IMPLEMENTED",
        "SUMMARY":summary,
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "PROMOTION_ALLOWED":False,
        "EDGE":"NOT_PROVEN",
        "CAUSALITY":"NOT_PROVEN",
        "EXPORT_READY":True,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (out/"research_grid_jobs.json").write_text(json.dumps(jobs,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"research_grid_summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P11.5_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    return manifest

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
