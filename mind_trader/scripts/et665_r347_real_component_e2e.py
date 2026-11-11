"""ET665.R347: execute the actual S20/S21 gate on an independently hashed CSV.

This is not a market-data provider or a synthetic fixture generator.
PAPER_ONLY. No broker/network imports.
"""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    from .et665_r341_s20_s21_causal_gate import validate_file
except ImportError:
    from et665_r341_s20_s21_causal_gate import validate_file

def run(csv_path: Path, expected_sha256: str, evidence_path: Path):
    if not isinstance(expected_sha256, str) or len(expected_sha256) != 64 or any(c not in "0123456789abcdef" for c in expected_sha256):
        raise ValueError("independent_sha256_required")
    if not csv_path.is_file() or csv_path.is_symlink():
        raise ValueError("regular_input_file_required")
    if evidence_path.resolve() == csv_path.resolve():
        raise ValueError("evidence_must_not_overwrite_input")
    result = validate_file(csv_path, expected_sha256)
    report = {
        "mission": "ET665.R347",
        "status": "STRUCTURAL_ONLY_NOT_OOS_CERTIFIED",
        "source_kind": "OPERATOR_SUPPLIED_NOT_INDEPENDENTLY_PROVEN",
        "component": "mind_trader/scripts/et665_r341_s20_s21_causal_gate.py",
        "input_sha256": result["input_sha256"],
        "rows": result["rows"],
        "validated": result["validated"],
        "mode": "PAPER_ONLY",
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return report

def main():
    p = argparse.ArgumentParser()
    p.add_argument("csv_path", type=Path)
    p.add_argument("--expected-sha256", required=True)
    p.add_argument("--evidence", required=True, type=Path)
    args = p.parse_args()
    try:
        report = run(args.csv_path, args.expected_sha256, args.evidence)
        print(json.dumps({"status": report["status"], "rows": report["rows"], "input_sha256": report["input_sha256"]}, sort_keys=True))
    except (ValueError, OSError) as exc:
        print(json.dumps({"status": "BLOCKED", "reason": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2
    return 0

if __name__ == "__main__":
    sys.exit(main())
