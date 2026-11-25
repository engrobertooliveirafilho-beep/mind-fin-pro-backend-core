from app.p9_continuous_research_runtime.engine import run_cycle, STEPS

def test_p96_does_not_claim_listed_steps_were_executed():
    cycle = run_cycle("TEST_CYCLE")
    assert cycle["status"] == "BLOCKED_DEPENDENCIES_NOT_CERTIFIED"
    assert cycle["steps"] == STEPS
    assert set(cycle["step_statuses"]) == set(STEPS)
    assert set(cycle["step_statuses"].values()) == {"BLOCKED_NOT_EXECUTED"}
    assert cycle["export_ready"] is False

def test_p96_runtime_blocks_live_and_broker():
    cycle = run_cycle("TEST_LOCK")
    assert cycle["live"] == "FORBIDDEN"
    assert cycle["real_broker"] == "DISABLED"
    assert cycle["promotion_allowed"] is False

def test_p96_manifest_written_as_blocked():
    import json
    from pathlib import Path
    run_cycle("TEST_REPORT")
    path = Path("reports/P9.6_CONTINUOUS_RESEARCH_RUNTIME/P9.6_manifest.json")
    report = json.loads(path.read_text(encoding="utf-8"))
    assert report["status"] == "BLOCKED_DEPENDENCIES_NOT_CERTIFIED"
