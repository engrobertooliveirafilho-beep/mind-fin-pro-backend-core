import json
from pathlib import Path
from datetime import datetime, timezone
from ..p11_multi_market_research_grid.engine import build_grid, summarize

def evaluate_scale_readiness(grid_summary):
    total=grid_summary.get("total_jobs",0)
    queued=grid_summary.get("queued",0)
    if type(total) is not int or type(queued) is not int or not 0<=queued<=total:
        raise ValueError('invalid job counts')
    ratio=(queued/total) if total else 0
    return {
        "total_jobs":total,
        "queued_jobs":queued,
        "research_coverage_ratio":round(ratio,6),
        "scale_ready":False,
        "reported_queue_ratio":round(ratio,6),
        "validation_executed":False,
        "edge_evidence_at_scale":"BLOCKED_PENDING_VERIFIED_EXECUTION",
        "live":"FORBIDDEN",
        "real_broker":"DISABLED",
        "promotion_allowed":False
    }

def run():
    out=Path("reports/P11.6_EDGE_EVIDENCE_AT_SCALE")
    out.mkdir(parents=True,exist_ok=True)
    summary=summarize(build_grid())
    readiness=evaluate_scale_readiness(summary)
    manifest={
        "STATUS":"P11.6_EDGE_EVIDENCE_AT_SCALE_IMPLEMENTED",
        "READINESS":readiness,
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "EDGE":"NOT_PROVEN",
        "CAUSALITY":"NOT_PROVEN",
        "PROMOTION_ALLOWED":False,
        "NEXT":"LOAD_CERTIFIED_REAL_DATA",
        "EXPORT_READY":True,
        "generated_at":datetime.now(timezone.utc).isoformat()
    }
    (out/"scale_readiness.json").write_text(json.dumps(readiness,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P11.6_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    return manifest

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
