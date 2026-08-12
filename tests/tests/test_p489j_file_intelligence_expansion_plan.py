import json
from pathlib import Path

def test_p489j_file_intelligence_expansion_plan():
    plan = json.loads(
        Path("runtime/file_intelligence/file_intelligence_expansion_plan.json").read_text(encoding="utf-8")
    )

    assert plan["milestone"] == "P4.89J COMPLETE"
    assert plan["mode"] == "PLAN_ONLY"
    assert plan["physical_move"] == "FORBIDDEN"
    assert plan["delete"] == "FORBIDDEN"
    assert plan["decision_for_p490"]["ready_for_p490"] is True
    assert "p0_parsers" in plan
    assert plan["next"] == "P4.90 SOVEREIGN TECHNICAL CAPACITY CERTIFICATION"
