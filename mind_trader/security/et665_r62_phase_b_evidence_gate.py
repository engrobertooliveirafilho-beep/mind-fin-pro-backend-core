"""ET665 R62: fail-closed Phase B evidence gate; offline, stdlib only."""
import argparse
import hashlib
import json
from pathlib import Path

REQUIRED = ("drive_manifest", "git_manifest", "reconciliation", "p77_p79_isolation", "security_review")

def assess(data, root):
    checks = {}
    for name in REQUIRED:
        entry = data.get(name)
        if not isinstance(entry, dict):
            checks[name] = "MISSING"
            continue
        path, expected = entry.get("path"), entry.get("sha256")
        if not isinstance(path, str) or not isinstance(expected, str) or len(expected) != 64:
            checks[name] = "INVALID_METADATA"
            continue
        try:
            int(expected, 16)
            file = (root / path).resolve()
            if not file.is_relative_to(root.resolve()) or not file.is_file():
                checks[name] = "MISSING_OR_UNSAFE_PATH"
            elif hashlib.sha256(file.read_bytes()).hexdigest() != expected.lower():
                checks[name] = "HASH_MISMATCH"
            elif entry.get("approved") is not True:
                checks[name] = "NOT_APPROVED"
            else:
                checks[name] = "EVIDENCE_PRESENT"
        except (ValueError, OSError):
            checks[name] = "INVALID_EVIDENCE"
    return {"schema": "ET665_R62_PHASE_B_GATE_V1", "checks": checks,
            "evidence_complete": all(x == "EVIDENCE_PRESENT" for x in checks.values()),
            "phase_b_certified": False,
            "note": "Completeness alone never certifies safety; human/technical decision required.",
            "real_orders": "FORBIDDEN", "ftmo_real": "FORBIDDEN"}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--evidence-json", type=Path, required=True)
    p.add_argument("--root", type=Path, required=True)
    a = p.parse_args()
    try:
        data = json.loads(a.evidence_json.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("not object")
        result = assess(data, a.root)
    except (ValueError, OSError) as exc:
        result = {"phase_b_certified": False, "error": type(exc).__name__, "real_orders": "FORBIDDEN"}
    print(json.dumps(result, sort_keys=True))
    return 0 if result.get("evidence_complete") else 2

if __name__ == "__main__":
    raise SystemExit(main())
