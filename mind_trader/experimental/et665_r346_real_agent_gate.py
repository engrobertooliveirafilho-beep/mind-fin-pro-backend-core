"""ET665.R346 — strict REAL-module HP19 candidate execution gate.

Runs only in an offline, read-only Docker container. Does not install,
mock, fabricate or synthesize agent implementations. Zero agents passing
is a legitimate FAIL_CLOSED result, not an error to conceal.
"""
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import sys

DISPATCH_PATH = Path(__file__).with_name("et665_r340_safe_agent_dispatch.py")

def load_dispatch():
    import importlib.util
    spec = importlib.util.spec_from_file_location("et665_r346_dispatch", DISPATCH_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def verify_one(name, payload, dispatch):
    module = importlib.import_module("app.agents." + name)
    origin = getattr(module, "__file__", None)
    if not origin or not Path(origin).is_file():
        raise RuntimeError("no on-disk agent implementation")
    source = Path(origin).read_bytes()
    if not source:
        raise RuntimeError("empty agent source")
    result = dispatch.run_agent(name, payload)
    if result.get("component") != payload["component"]:
        raise RuntimeError("component identity missing or incorrect")
    if result.get("input_sha256") != payload["input_sha256"]:
        raise RuntimeError("input lineage not proven")
    output = result.get("output")
    if not isinstance(output, dict) or not output:
        raise RuntimeError("concrete output payload missing")
    serialized = json.dumps(output, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    expected_hash = hashlib.sha256(serialized).hexdigest()
    if result.get("output_sha256") != expected_hash:
        raise RuntimeError("output hash does not match concrete output")
    if not isinstance(result.get("processed_items"), int) or result["processed_items"] < 1:
        raise RuntimeError("no real processing evidence")
    return {"agent_id": name, "source_sha256": hashlib.sha256(source).hexdigest(),
            "input_sha256": payload["input_sha256"], "output_sha256": result["output_sha256"],
            "processed_items": result["processed_items"], "status": "PASS"}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--evidence", required=True)
    args = p.parse_args()
    evidence = Path(args.evidence)
    evidence.mkdir(parents=True, exist_ok=True)
    dispatch = load_dispatch()
    payload = {"component": "monthly_cashflow",
               "revenue": "10000.00", "fixed_costs": "4000.00",
               "variable_costs": "2000.00", "cash_balance": "5000.00"}
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["input_sha256"] = hashlib.sha256(canonical).hexdigest()
    records = []
    for name in dispatch.AGENT_MODULES:
        try:
            records.append(verify_one(name, payload, dispatch))
        except Exception as exc:
            records.append({"agent_id": name, "status": "BLOCKED",
                            "reason": type(exc).__name__ + ": " + str(exc)})
    passed = sum(r["status"] == "PASS" for r in records)
    report = {"status": "PASS" if passed == 19 else "FAIL_CLOSED",
              "candidate_agents": len(records), "verified": passed,
              "hp19_membership": "NOT_VERIFIED", "hp19_certified": False,
              "phase_b_certified": False, "real_orders": "FORBIDDEN",
              "results": records}
    evidence.joinpath("r346_candidate_agent_gate.json").write_text(
        json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"status": report["status"], "verified": passed,
                      "total": len(records), "evidence": str(evidence)}))
    return 0 if passed == 19 else 1

if __name__ == "__main__":
    sys.exit(main())
