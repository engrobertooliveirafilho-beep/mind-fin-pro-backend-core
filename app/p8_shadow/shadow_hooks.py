import time
import uuid
from typing import Any, Dict
from .feature_flags import load_p8_feature_flags
from .telemetry import append_shadow_log
from .diff_engine import build_decision_diff

def run_hierarchical_planner_shadow(payload: Any, *, log_path: str | None = None) -> Dict[str, Any]:
    flags = load_p8_feature_flags()
    request_id = str(uuid.uuid4())
    started = time.perf_counter()

    if not flags.enable_hierarchical_planner or flags.hierarchical_mode != "SHADOW":
        return {"status": "SKIPPED", "reason": "planner_shadow_disabled", "runtime_modified": False}

    try:
        result = {
            "request_id": request_id,
            "capability": "HIERARCHICAL_PLANNING",
            "mode": "SHADOW",
            "plan": [],
            "runtime_modified": False,
        }
        latency = (time.perf_counter() - started) * 1000
        append_shadow_log(request_id=request_id, module="hierarchical_planner", status="PASS", latency_ms=latency, execution_mode="SHADOW", result=result, log_path=log_path)
        return result
    except Exception as exc:
        latency = (time.perf_counter() - started) * 1000
        append_shadow_log(request_id=request_id, module="hierarchical_planner", status="ERROR", latency_ms=latency, execution_mode="SHADOW", error=str(exc), log_path=log_path)
        return {"status": "ERROR", "error": str(exc), "runtime_modified": False}

def run_oversight_shadow(runtime_output: Any, *, log_path: str | None = None) -> Dict[str, Any]:
    flags = load_p8_feature_flags()
    request_id = str(uuid.uuid4())
    started = time.perf_counter()

    if not flags.enable_oversight or flags.oversight_mode != "SHADOW":
        return {"status": "SKIPPED", "reason": "oversight_shadow_disabled", "runtime_modified": False}

    try:
        oversight_decision = {"decision": "ALLOW", "mode": "SHADOW", "blocking": False}
        diff = build_decision_diff(request_id=request_id, runtime_decision=runtime_output, oversight_decision=oversight_decision, confidence=1.0, reason="shadow_only")
        latency = (time.perf_counter() - started) * 1000
        append_shadow_log(request_id=request_id, module="oversight", status="PASS", latency_ms=latency, execution_mode="SHADOW", result=diff, log_path=log_path)
        return diff
    except Exception as exc:
        latency = (time.perf_counter() - started) * 1000
        append_shadow_log(request_id=request_id, module="oversight", status="ERROR", latency_ms=latency, execution_mode="SHADOW", error=str(exc), log_path=log_path)
        return {"status": "ERROR", "error": str(exc), "runtime_modified": False}
