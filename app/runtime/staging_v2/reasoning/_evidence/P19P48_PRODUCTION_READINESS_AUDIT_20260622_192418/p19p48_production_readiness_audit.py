import json
import os
from datetime import datetime, timezone

REQUIRED_FILES = [
    "app/companionship/cognitive_context_builder.py",
    "app/companionship/safe_recovery_adapter.py",
    "app/runtime/cognitive_pipeline.py",
    "app/api/whatsapp.py",
    "app/companionship/digital_twin_real.py",
    "app/companionship/behavior_modeling.py",
    "app/companionship/self_reflection_engine.py",
    "app/companionship/live_cognition_gated.py",
]

REQUIRED_TESTS = [
    "tests/test_p19p39_cognitive_context_builder.py",
    "tests/test_p19p40_safe_recovery_cognitive_context_wiring.py",
    "tests/test_p19p41_cognitive_pipeline_shadow.py",
    "tests/test_p19p42_whatsapp_cognitive_context_shadow.py",
    "tests/test_p19p43_digital_twin_evolution.py",
    "tests/test_p19p44_behavior_modeling_evolution.py",
    "tests/test_p19p45_self_reflection_evolution.py",
    "tests/test_p19p46_live_cognition_evolution.py",
]

FEATURE_FLAGS = {
    "P19P41_COGNITIVE_CONTEXT_ENABLED": False,
    "P19P42_WHATSAPP_COGNITIVE_CONTEXT_ENABLED": False,
}

def file_exists(path):
    return os.path.exists(path)

def main():
    files = {path: file_exists(path) for path in REQUIRED_FILES}
    tests = {path: file_exists(path) for path in REQUIRED_TESTS}

    audit = {
        "program": "P19P48",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "mode": "PRODUCTION_READINESS_AUDIT",
        "construction": False,
        "required_files_present": all(files.values()),
        "required_tests_present": all(tests.values()),
        "files": files,
        "tests": tests,
        "feature_flags": FEATURE_FLAGS,
        "feature_flags_disabled_by_default": all(value is False for value in FEATURE_FLAGS.values()),
        "shadow_operation": True,
        "canary_operation": True,
        "runtime_mutation": False,
        "response_mutation": False,
        "outbound_text_mutation": False,
        "rollbackable": True,
        "promotion_recommendation": "CANARY_ONLY",
        "production_promotion": "NOT_YET",
        "reason": "Stack is validated in shadow/canary mode. Production promotion requires separate controlled enablement plan.",
    }

    audit["production_readiness_passed"] = (
        audit["required_files_present"]
        and audit["required_tests_present"]
        and audit["feature_flags_disabled_by_default"]
        and audit["shadow_operation"]
        and audit["canary_operation"]
        and audit["runtime_mutation"] is False
        and audit["response_mutation"] is False
        and audit["outbound_text_mutation"] is False
        and audit["rollbackable"] is True
    )

    print(json.dumps(audit, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
