import json
from pathlib import Path
from datetime import datetime, UTC
from app.p11_multi_market_research_grid.engine import run as run_grid

def evaluate_scale_readiness(grid_summary):
    total=grid_summary.get("total_jobs",0)
    queued=grid_summary.get("queued",0)
    ratio=(queued/total) if total else 0
    return {
        "total_jobs":total,
        "queued_jobs":queued,
        "research_coverage_ratio":round(ratio,6),
        "scale_ready":ratio>=0.25,
        "edge_evidence_at_scale":"BLOCKED_PENDING_CERTIFIED_DATA" if ratio<0.25 else "READY_FOR_MASSIVE_RESEARCH",
        "live":"FORBIDDEN",
        "real_broker":"DISABLED",
        "promotion_allowed":False
    }

def run():
    out=Path("reports/P11.6_EDGE_EVIDENCE_AT_SCALE")
    out.mkdir(parents=True,exist_ok=True)
    run_grid()
    summary=json.loads(Path("reports/P11.5_MULTI_MARKET_RESEARCH_GRID/research_grid_summary.json").read_text(encoding="utf-8"))
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
        "generated_at":datetime.now(UTC).isoformat()
    }
    (out/"scale_readiness.json").write_text(json.dumps(readiness,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P11.6_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    return manifest

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
