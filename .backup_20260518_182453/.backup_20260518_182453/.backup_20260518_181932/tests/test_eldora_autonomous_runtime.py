from app.eldora.core.autonomous_planner import create_plan
from app.eldora.core.governor_engine import consume_budget
from app.eldora.core.checkpoint_engine import create_checkpoint

def test_create_plan():
    plan = create_plan("validate_system")
    assert plan["status"] == "planned"

def test_governor_budget():
    result = consume_budget(1)
    assert result["allowed"] is True

def test_checkpoint():
    cp = create_checkpoint({"runtime":"eldora"})
    assert cp["runtime_state"]["runtime"] == "eldora"
