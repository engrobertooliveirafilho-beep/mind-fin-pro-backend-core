"""ET665.R52: source-based classification of subprocess findings, not authorization."""
import argparse
import csv
import json
from collections import Counter
from pathlib import Path

from et665_r47_execution_path_inventory import inventory

P15 = {
    "app/p1516_multi_family_combo_backtest_executor/engine.py",
    "app/p1525b_cloud_dataset_reconstruction_fix/engine.py",
    "app/p153_p155_profit_market_data_pipeline/engine.py",
    "app/p156_p1510_real_edge_research_runtime/engine.py",
}
SECURITY_RUNNERS = {
    "security/et665_mb_phase_b_runner.py",
    "security/et665_mb_r8_consolidated_runner.py",
}
GIT_AUDITS = {
    "security/et665_r23_full_tree_inventory.py",
    "security/et665_r28_mirror_drift_audit.py",
}


def classify(row):
    path = row["path"]
    if path in P15:
        return "P15_DRIVE_READ_TO_LOCAL", "SOURCE_REVIEWED_TESTED_BOUNDARY", "R51 mock regression passed; still requires argv/path adversarial review"
    if path == "app/audits/institutional_healthcheck.py":
        return "PYTEST_HEALTHCHECK", "SOURCE_REVIEWED_NOT_CERTIFIED", "Python pytest invocation; caller-controlled test_path requires path restriction"
    if path in SECURITY_RUNNERS:
        return "PYTEST_EVIDENCE_RUNNER", "SOURCE_REVIEWED_NOT_CERTIFIED", "Fixed pytest list and temp output guard; environment and filesystem isolation unverified"
    if path in GIT_AUDITS:
        return "GIT_READ_ONLY_AUDIT", "SOURCE_REVIEWED_NOT_CERTIFIED", "Git object inspection; repository trust and subprocess boundaries unverified"
    if path.startswith("tests/"):
        return "TEST_GIT_SUBPROCESS", "TEST_ONLY_REVIEW_PENDING", "Git inspection inside tests; not a trading execution authorization"
    return "UNCLASSIFIED", "BLOCKED", "Manual review required"


def report(root, out):
    scanned, findings = inventory(root)
    rows = []
    for item in findings:
        category, status, rationale = classify(item)
        rows.append({**item, "purpose": category, "review_status": status, "rationale": rationale})
    out.mkdir(parents=True, exist_ok=True)
    with (out / "R52_PROCESS_EVIDENCE.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["path", "line", "category", "symbol", "sha256", "purpose", "review_status", "rationale"])
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "mission": "ET665.R52", "files_scanned": scanned, "findings_total": len(rows),
        "categories": dict(sorted(Counter(x["purpose"] for x in rows).items())),
        "unclassified": sum(x["purpose"] == "UNCLASSIFIED" for x in rows),
        "authorized_execution": 0, "security_certification": "NOT_GRANTED",
        "phase_b": "OPEN", "real_orders": "FORBIDDEN", "ftmo_real": "FORBIDDEN",
        "scope": "Working-tree AST only; source-reviewed categories are not runtime attestations",
    }
    (out / "R52_SUMMARY.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if not args.root.is_dir():
        parser.error("root does not exist")
    report(args.root.resolve(), args.out.resolve())


if __name__ == "__main__":
    main()
