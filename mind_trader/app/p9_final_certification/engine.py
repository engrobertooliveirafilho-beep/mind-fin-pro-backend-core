import json
import datetime
from pathlib import Path

REQUIRED_REPORTS = [
    "reports/P9.1_DATA_EXPANSION_ENGINE/P9.1_STATE_SNAPSHOT.json",
    "reports/P9.2_GENOME_EXPLOSION_ENGINE/P9.2_manifest.json",
    "reports/P9.3_MASSIVE_BACKTEST_GRID/P9.3_manifest.json",
    "reports/P9.4_DNA_EXTRACTION_ENGINE/P9.4_manifest.json",
    "reports/P9.5_EDGE_DISCOVERY_FACTORY/P9.5_manifest.json",
    "reports/P9.6_CONTINUOUS_RESEARCH_RUNTIME/P9.6_manifest.json",
    "reports/P9.7_RESEARCH_COMMAND_CENTER/P9.7_manifest.json"
]

REQUIRED_FUNCTIONAL_GATES = {
    "real_market_data_lineage": False,
    "real_backtest_execution": False,
    "walk_forward_execution": False,
    "monte_carlo_execution": False,
    "robustness_committee_execution": False,
    "paper_candidate_provenance": False,
    "end_to_end_test_evidence": False
}

def certify():
    # Report presence is inventory only. It cannot certify code execution,
    # data lineage, statistical validation, or a functional PAPER pipeline.
    reports = {path: Path(path).is_file() for path in REQUIRED_REPORTS}
    cert = {
        "P9_STATE_SNAPSHOT": {
            "STATUS": "P9_CERTIFICATION_BLOCKED",
            "BASE": "P8.100_PAPER_RESEARCH_V1_CERTIFIED",
            "REPORTS_PRESENT": reports,
            "FUNCTIONAL_GATES": dict(REQUIRED_FUNCTIONAL_GATES),
            "MODULES_CERTIFIED": [],
            "MODULES_PENDING": [
                "P9.1_DATA_EXPANSION_ENGINE",
                "P9.2_GENOME_EXPLOSION_ENGINE",
                "P9.3_MASSIVE_BACKTEST_GRID",
                "P9.4_DNA_EXTRACTION_ENGINE",
                "P9.5_EDGE_DISCOVERY_FACTORY",
                "P9.6_CONTINUOUS_RESEARCH_RUNTIME",
                "P9.7_RESEARCH_COMMAND_CENTER"
            ],
            "BLOCKING_REASONS": [
                "P9.1_HAS_DATASET_SLOTS_BUT_NO_VERIFIED_REAL_DATA_LINEAGE",
                "P9.3_PREVIOUSLY_GENERATED_RANDOM_METRICS_INSTEAD_OF_BACKTESTS",
                "P9.5_PREVIOUSLY_ACCEPTED_UNVERIFIED_METRICS",
                "P9.6_PREVIOUSLY_REPORTED_STEPS_WITHOUT_EXECUTING_THEM",
                "NO_REPRODUCIBLE_WALK_FORWARD_MONTE_CARLO_OR_ROBUSTNESS_EVIDENCE",
                "NO_VERIFIED_END_TO_END_TEST_EVIDENCE"
            ],
            "LIVE": "FORBIDDEN",
            "PRODUCTION": "BLOCKED",
            "REAL_BROKER": "DISABLED",
            "FTMO_REAL": "FORBIDDEN",
            "EDGE": "NOT_PROVEN",
            "CAUSALITY": "NOT_PROVEN",
            "PROMOTION": "FORBIDDEN_PENDING_FUNCTIONAL_CERTIFICATION",
            "NEXT_PHASE": "P9_FUNCTIONAL_REMEDIATION",
            "EXPORT_READY": False,
            "generated_at": datetime.datetime.now(datetime.UTC).isoformat()
        }
    }
    out = Path("reports/P9.100_FINAL_CERTIFICATION")
    out.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(cert, indent=2, ensure_ascii=False)
    (out / "P9_STATE_SNAPSHOT.json").write_text(payload, encoding="utf-8")
    (out / "P9.100_final_certification.json").write_text(payload, encoding="utf-8")
    return cert

if __name__ == "__main__":
    print(json.dumps(certify(), indent=2, ensure_ascii=False))
