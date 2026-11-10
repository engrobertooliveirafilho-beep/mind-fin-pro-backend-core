"""ET665.R391: strict, offline evidence gate for 16 fronts and 19 HP19 executors.
Never infers certification from commits, fixture tests, or reported status.
No network, broker, or trading dependencies. Python 3.11 stdlib only.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

HEX = re.compile(r"^[0-9a-f]{64}$")
FRONTS = tuple(f"FRONT_{i:02d}" for i in range(1, 17))
AGENTS = tuple(f"HP19_{i:02d}" for i in range(1, 20))


def evaluate(root, manifest):
    root = Path(root).resolve(strict=True)
    doc = json.loads(Path(manifest).read_text(encoding="utf-8"))
    if set(doc) != {"schema", "component", "fronts", "agents"} or doc["schema"] != "ET665_R391_EVIDENCE_V1":
        raise ValueError("SCHEMA_INVALID")
    if set(doc["fronts"]) != set(FRONTS) or set(doc["agents"]) != set(AGENTS):
        raise ValueError("COVERAGE_INCOMPLETE")
    component = doc["component"]
    if not isinstance(component, dict) or set(component) != {"path", "sha256"}:
        raise ValueError("COMPONENT_INVALID")
    def verified(record):
        if not isinstance(record, dict) or set(record) != {"path", "sha256", "result"}:
            return False
        if record["result"] != "PASS":
            return False
        path, digest = record["path"], record["sha256"]
        if not isinstance(path, str) or not isinstance(digest, str) or not HEX.fullmatch(digest):
            return False
        if Path(path).is_absolute() or ".." in Path(path).parts:
            return False
        target = root / path
        if target.is_symlink() or not target.is_file() or not target.resolve().is_relative_to(root):
            return False
        return hashlib.sha256(target.read_bytes()).hexdigest() == digest
    if not isinstance(component["path"], str) or not isinstance(component["sha256"], str):
        raise ValueError("COMPONENT_INVALID")
    if not HEX.fullmatch(component["sha256"]):
        raise ValueError("COMPONENT_HASH_INVALID")
    cp = root / component["path"]
    if Path(component["path"]).is_absolute() or ".." in Path(component["path"]).parts or cp.is_symlink() or not cp.is_file() or not cp.resolve().is_relative_to(root):
        raise ValueError("COMPONENT_PATH_INVALID")
    if hashlib.sha256(cp.read_bytes()).hexdigest() != component["sha256"]:
        raise ValueError("COMPONENT_HASH_MISMATCH")
    fronts = {k: verified(v) for k, v in doc["fronts"].items()}
    agents = {k: verified(v) for k, v in doc["agents"].items()}
    return {"fronts_pass": sum(fronts.values()), "agents_pass": sum(agents.values()),
            "fronts_total": 16, "agents_total": 19,
            "evidence_complete": all(fronts.values()) and all(agents.values()),
            "certified": False,
            "real_component_hash_verified": True,
            "warning": "Hash-matched PASS evidence alone does not prove behavioral execution or independence."}


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 2:
        print("usage: python -m mind_trader.research.et665_r391_evidence_gate ROOT MANIFEST")
        return 2
    try:
        result = evaluate(*args)
        print(json.dumps(result, sort_keys=True))
        return 0 if result["evidence_complete"] else 1
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        print(json.dumps({"certified": False, "error": str(exc)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
