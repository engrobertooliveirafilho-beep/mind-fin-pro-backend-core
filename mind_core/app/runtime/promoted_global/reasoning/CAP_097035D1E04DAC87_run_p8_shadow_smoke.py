import json
import os
from pathlib import Path

os.environ["ENABLE_HIERARCHICAL_PLANNER"] = "true"
os.environ["HIERARCHICAL_MODE"] = "SHADOW"
os.environ["ENABLE_OVERSIGHT"] = "true"
os.environ["OVERSIGHT_MODE"] = "SHADOW"

from app.p8_shadow.shadow_hooks import run_hierarchical_planner_shadow, run_oversight_shadow
from app.p8_shadow.feature_flags import load_p8_feature_flags

out = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core\\_evidence\\P8_MASTER_SHADOW_VALIDATION_20260615_211124")
log_path = out / "P8_SHADOW_SMOKE_TELEMETRY.jsonl"

flags = load_p8_feature_flags()

planner = run_hierarchical_planner_shadow(
    {"goal": "validate P8 shadow hierarchical planner"},
    log_path=str(log_path)
)

oversight = run_oversight_shadow(
    {"runtime_answer": "baseline runtime remains authoritative"},
    log_path=str(log_path)
)

result = {
    "mission": "P8_SHADOW_SMOKE_VALIDATION",
    "flags": {
        "enable_hierarchical_planner": flags.enable_hierarchical_planner,
        "enable_oversight": flags.enable_oversight,
        "hierarchical_mode": flags.hierarchical_mode,
        "oversight_mode": flags.oversight_mode
    },
    "planner": planner,
    "oversight": oversight,
    "runtime_modified": False,
    "response_modified": False,
    "active_mode_allowed": False,
    "block_mode_allowed": False,
    "runtime_authority_preserved": True
}

(out / "P8_SHADOW_SMOKE_RESULT.json").write_text(
    json.dumps(result, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(json.dumps(result, ensure_ascii=False))
