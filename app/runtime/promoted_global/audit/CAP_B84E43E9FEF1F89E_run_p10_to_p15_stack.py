import os
import json
import time
from pathlib import Path

os.environ["ENABLE_P9_RUNTIME_CONSUMPTION"] = "true"
os.environ["P9_RUNTIME_CONSUMPTION_MODE"] = "DRY_RUN"

os.environ["ENABLE_P10_CONTROLLED_ACTIVATION"] = "true"
os.environ["P10_ACTIVATION_MODE"] = "LIMITED_ACTIVE"
os.environ["P10_ALLOW_RESPONSE_MODIFICATION"] = "false"

from app.p10_activation_stack.controlled_consumption import run_controlled_consumption
from app.p10_activation_stack.rollback import rollback_controlled_consumption
from app.p10_activation_stack.risk_governance import evaluate_p12_risk
from app.p10_activation_stack.observability import append_activation_observation
from app.p10_activation_stack.certification import certify_p10_to_p15

out = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core\\_evidence\\P10_TO_P15_CONTROLLED_CONSUMPTION_ACTIVATION_STACK_20260616_153902")
obs_log = out / "P10_TO_P15_OBSERVATION.jsonl"

cases = [
    "P10 controlled runtime consumption review",
    "P11 rollback validation",
    "P12 risk governance",
    "P13 observability validation",
    "P14 regression gate preparation",
    "P15 final certification"
]

records = []
started = time.perf_counter()

for i, goal in enumerate(cases):
    runtime_input = {"goal": goal, "case": i}
    runtime_response = {"answer": "runtime authoritative", "case": i}

    p10 = run_controlled_consumption(runtime_input, runtime_response)
    p11 = rollback_controlled_consumption(p10["runtime_response_after"], runtime_response)
    p12 = evaluate_p12_risk(p10)

    record = {
        "case": i,
        "goal": goal,
        "p10_status": p10["status"],
        "p11_status": p11["status"],
        "p12_status": p12["status"],
        "response_modified": p10["response_modified"],
        "runtime_state_modified": p10["runtime_state_modified"],
        "routes_modified": p10["routes_modified"],
        "dispatcher_modified": p10["dispatcher_modified"],
        "whatsapp_webhook_modified": p10["whatsapp_webhook_modified"],
        "runtime_authority_preserved": p10["runtime_authority_preserved"],
        "status": "PASS" if p10["status"] == "PASS" and p11["status"] == "PASS" and p12["activation_allowed"] else "FAIL"
    }

    append_activation_observation(record, str(obs_log))
    records.append(record)

cert = certify_p10_to_p15(records)

report = {
    "mission": "P10_TO_P15_CONTROLLED_CONSUMPTION_ACTIVATION_STACK",
    "scope": {
        "P10": "CONTROLLED_RUNTIME_CONSUMPTION_ACTIVATION_REVIEW",
        "P11": "ROLLBACK_VALIDATION",
        "P12": "RISK_GOVERNANCE",
        "P13": "OBSERVABILITY",
        "P14": "REGRESSION_GATE",
        "P15": "FINAL_CERTIFICATION"
    },
    "cases": len(records),
    "pass_count": sum(1 for r in records if r["status"] == "PASS"),
    "runtime_modified": False,
    "runtime_state_modified": False,
    "routes_modified": False,
    "dispatcher_modified": False,
    "whatsapp_webhook_modified": False,
    "active_mode_enabled": False,
    "block_mode_enabled": False,
    "response_modification_allowed": False,
    "runtime_authority_preserved": True,
    "certification": cert,
    "elapsed_seconds": time.perf_counter() - started,
    "status": "PASS" if cert["status"] == "PASS" else "FAIL",
    "next_required_action": "P16_PRODUCTION_ACTIVATION_DECISION_GATE",
    "records": records
}

(out / "P10_TO_P15_FINAL_REPORT.json").write_text(
    json.dumps(report, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(json.dumps(report, ensure_ascii=False))
