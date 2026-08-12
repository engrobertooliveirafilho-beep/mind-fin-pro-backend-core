import json
from pathlib import Path

from app.p8_shadow.feature_flags import load_p8_feature_flags
from app.p8_shadow.shadow_hooks import run_hierarchical_planner_shadow, run_oversight_shadow
from app.p8_shadow.diff_engine import build_decision_diff

def test_p8_flags_default_off(monkeypatch):
    monkeypatch.delenv("ENABLE_HIERARCHICAL_PLANNER", raising=False)
    monkeypatch.delenv("ENABLE_OVERSIGHT", raising=False)
    flags = load_p8_feature_flags()
    assert flags.enable_hierarchical_planner is False
    assert flags.enable_oversight is False
    assert flags.hierarchical_mode == "OFF"
    assert flags.oversight_mode == "OFF"

def test_p8_planner_shadow_disabled_by_default():
    result = run_hierarchical_planner_shadow({"goal": "test"})
    assert result["status"] == "SKIPPED"
    assert result["runtime_modified"] is False

def test_p8_oversight_shadow_disabled_by_default():
    result = run_oversight_shadow({"answer": "ok"})
    assert result["status"] == "SKIPPED"
    assert result["runtime_modified"] is False

def test_p8_planner_shadow_enabled(monkeypatch, tmp_path):
    monkeypatch.setenv("ENABLE_HIERARCHICAL_PLANNER", "true")
    monkeypatch.setenv("HIERARCHICAL_MODE", "SHADOW")
    log = tmp_path / "shadow.jsonl"
    result = run_hierarchical_planner_shadow({"goal": "x"}, log_path=str(log))
    assert result["capability"] == "HIERARCHICAL_PLANNING"
    assert result["mode"] == "SHADOW"
    assert result["runtime_modified"] is False
    assert log.exists()

def test_p8_oversight_shadow_enabled(monkeypatch, tmp_path):
    monkeypatch.setenv("ENABLE_OVERSIGHT", "true")
    monkeypatch.setenv("OVERSIGHT_MODE", "SHADOW")
    log = tmp_path / "shadow.jsonl"
    result = run_oversight_shadow({"answer": "ok"}, log_path=str(log))
    assert result["mode"] == "SHADOW"
    assert result["response_modified"] is False
    assert result["runtime_authority_preserved"] is True
    assert log.exists()

def test_p8_diff_engine_preserves_runtime_authority():
    diff = build_decision_diff(
        request_id="r1",
        runtime_decision={"answer": "runtime"},
        oversight_decision={"decision": "ALLOW"},
        confidence=0.9,
        reason="test",
    )
    assert diff["runtime_authority_preserved"] is True
    assert diff["response_modified"] is False
    assert diff["mode"] == "SHADOW"
