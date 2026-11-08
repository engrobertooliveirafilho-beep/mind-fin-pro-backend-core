"""ET665.R50: offline triage of R47 static findings, without executing inspected files.

All subprocess and dynamic-execution findings remain unapproved pending source review.
No automatic security certification is inferred from the classification.
"""
import argparse
import ast
import csv
import json
from collections import Counter
from pathlib import Path

from et665_r47_execution_path_inventory import inventory

FIELDS = ("path", "line", "category", "symbol", "sha256", "priority", "disposition", "review_reason")


def classify(finding):
    category = finding["category"]
    if category == "DYNAMIC_EXEC":
        return "HIGH", "MANUAL_REVIEW", "Determine whether executable input is user-controlled; prohibit arbitrary execution"
    if category == "PROCESS_SPAWN":
        return "HIGH", "MANUAL_REVIEW", "Verify argv allowlist, shell=False, input origin, filesystem boundaries and no broker/Drive mutation"
    if category in {"MT5_IMPORT", "MT5_TERMINAL"}:
        return "CRITICAL", "BLOCK_PENDING_CERTIFICATION", "Uncertified terminal access must remain blocked before import"
    return "HIGH", "MANUAL_REVIEW", "Inspect original source and execution reachability"


def triage(root, out):
    scanned, findings = inventory(root)
    rows = []
    for finding in findings:
        priority, disposition, reason = classify(finding)
        rows.append({**finding, "priority": priority, "disposition": disposition, "review_reason": reason})
    out.mkdir(parents=True, exist_ok=True)
    with (out / "R50_TRIAGE.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "mission": "ET665.R50", "files_scanned": scanned, "findings_total": len(rows),
        "categories": dict(sorted(Counter(row["category"] for row in rows).items())),
        "dispositions": dict(sorted(Counter(row["disposition"] for row in rows).items())),
        "approved_for_execution": 0, "certification": "NOT_GRANTED",
        "phase_b": "OPEN", "real_orders": "FORBIDDEN", "ftmo_real": "FORBIDDEN",
        "scope_limit": "Python AST known symbols only; aliases and runtime dispatch not resolved",
    }
    (out / "R50_SUMMARY.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if not args.root.is_dir():
        parser.error("root does not exist")
    triage(args.root.resolve(), args.out.resolve())


if __name__ == "__main__":
    main()
