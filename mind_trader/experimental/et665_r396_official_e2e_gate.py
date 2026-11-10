"""ET665.R396: fail-closed audit of independently supplied HP19/Phase B E2E evidence.
This verifies evidence structure and file integrity, NOT historical equivalence by itself.
Offline, read-only, no broker or production integration.
"""
import argparse
import hashlib
import json
from pathlib import Path

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def verify(root, manifest):
    errors = []
    if not isinstance(manifest, dict):
        return {"status": "FAIL_CLOSED", "errors": ["manifest must be object"], "hp19": 0, "phase_b": 0}
    counts = {}
    for group, expected in (("hp19", 19), ("phase_b", 16)):
        entries = manifest.get(group)
        passed = 0
        ids = set()
        if not isinstance(entries, list) or len(entries) != expected:
            errors.append(f"{group}: expected exactly {expected} entries")
            entries = entries if isinstance(entries, list) else []
        for i, item in enumerate(entries):
            prefix = f"{group}[{i}]"
            if not isinstance(item, dict):
                errors.append(prefix + ": invalid entry")
                continue
            ident = item.get("historical_id")
            if not isinstance(ident, str) or not ident.strip() or ident in ids:
                errors.append(prefix + ": missing/duplicate historical_id")
                continue
            ids.add(ident)
            if item.get("status") != "PASS" or item.get("mode") != "PAPER" or item.get("synthetic") is not False:
                errors.append(prefix + ": requires PASS, PAPER and synthetic=false")
                continue
            if item.get("independent_review") is not True or not isinstance(item.get("reviewer"), str) or not item["reviewer"].strip():
                errors.append(prefix + ": independent review missing")
                continue
            valid = True
            for field in ("source", "input", "output", "execution_log"):
                record = item.get(field)
                if not isinstance(record, dict):
                    errors.append(prefix + f": {field} missing")
                    valid = False
                    continue
                name, sha = record.get("path"), record.get("sha256")
                if not isinstance(name, str) or not isinstance(sha, str) or len(sha) != 64:
                    errors.append(prefix + f": {field} invalid path/hash")
                    valid = False
                    continue
                candidate = root / name
                target = candidate.resolve()
                if not target.is_relative_to(root) or not target.is_file() or candidate.is_symlink():
                    errors.append(prefix + f": {field} missing/unsafe file")
                    valid = False
                    continue
                if digest(target) != sha.lower():
                    errors.append(prefix + f": {field} SHA256 mismatch")
                    valid = False
            if valid:
                passed += 1
        counts[group] = passed
    return {"status": "EVIDENCE_READY_FOR_HUMAN_REVIEW" if not errors and counts == {"hp19":19,"phase_b":16} else "FAIL_CLOSED",
            "hp19": counts["hp19"], "phase_b": counts["phase_b"], "errors": errors,
            "note": "No automatic historical equivalence or official certification."}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-root", required=True)
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()
    root = Path(args.evidence_root).resolve()
    manifest_path = Path(args.manifest).resolve()
    if not manifest_path.is_file() or not manifest_path.is_relative_to(root):
        print(json.dumps({"status":"FAIL_CLOSED","errors":["unsafe or missing manifest"]}))
        return 1
    try:
        result = verify(root, json.loads(manifest_path.read_text(encoding="utf-8")))
    except (OSError, ValueError) as exc:
        result = {"status":"FAIL_CLOSED","errors":[type(exc).__name__]}
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "EVIDENCE_READY_FOR_HUMAN_REVIEW" else 1

if __name__ == "__main__":
    raise SystemExit(main())
