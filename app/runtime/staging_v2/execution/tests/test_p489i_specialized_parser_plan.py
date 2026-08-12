import json
from pathlib import Path

def test_p489i_specialized_parser_plan():

    plan = json.loads(
        Path(
            "runtime/parser_planning/specialized_parser_implementation_plan.json"
        ).read_text(encoding="utf-8")
    )

    queue = json.loads(
        Path(
            "runtime/parser_planning/parser_priority_queue.json"
        ).read_text(encoding="utf-8")
    )

    assert plan["milestone"] == "P4.89I COMPLETE"
    assert plan["mode"] == "PLAN_ONLY"
    assert plan["approval_required"] is True
    assert plan["physical_move"] == "FORBIDDEN"
    assert plan["delete"] == "FORBIDDEN"

    assert queue["items_count"] >= 1
    assert isinstance(queue["items"], list)
