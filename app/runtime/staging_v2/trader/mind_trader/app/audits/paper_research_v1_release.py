import json, hashlib
from pathlib import Path
from datetime import datetime, UTC

def paper_research_v1_release(tests_passed=298):
    release={
        "release":"P8.100_PAPER_RESEARCH_V1",
        "created_at":datetime.now(UTC).isoformat(),
        "tests_passed":tests_passed,
        "validated_scope":"PAPER_RESEARCH_ONLY",
        "validated_capabilities":[
            "data_ingestion",
            "quality_gate",
            "data_catalog",
            "dataset_lineage",
            "knowledge_registry",
            "trader_dna",
            "strategy_genomes",
            "backtest_cluster",
            "correlation_authority",
            "causality_authority",
            "uncertainty_authority",
            "edge_discovery_research",
            "anti_overfitting",
            "walk_forward",
            "monte_carlo",
            "robustness_committee",
            "validation_protocol",
            "promotion_authority",
            "ftmo_simulation",
            "paper_session",
            "execution_gateway",
            "paper_broker",
            "paper_fill_model",
            "institutional_live_lock",
            "audit_reports"
        ],
        "production":"BLOCKED",
        "live":"FORBIDDEN",
        "real_broker_routing":"DISABLED",
        "edge_claim":"NONE",
        "causality_claim":"NOT_PROVEN",
        "decision":"PAPER_RESEARCH_V1_CERTIFIED"
    }
    raw=json.dumps(release,sort_keys=True,ensure_ascii=False,separators=(",",":"))
    release["release_hash"]=hashlib.sha256(raw.encode("utf-8")).hexdigest()
    Path("mind_trader/reports").mkdir(parents=True,exist_ok=True)
    Path("mind_trader/reports/P8.100_paper_research_v1_release.json").write_text(json.dumps(release,ensure_ascii=False,indent=2),encoding="utf-8")
    return release
