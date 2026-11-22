import pytest
from app.compliance import ComplianceEngine

SAFE = {"mode": "PAPER_ONLY", "real_orders": "FORBIDDEN", "ftmo_real": "FORBIDDEN"}


@pytest.mark.parametrize("action", ["paper_feedback", "paper_replay", "paper_validate"])
def test_explicit_paper_allowlist(action):
    decision = ComplianceEngine().check({**SAFE, "action": action})
    assert decision.allowed is True
    assert decision.policy == "default"


@pytest.mark.parametrize("action", [
    "forbidden_example", "qualquer_coisa", "real_order", "live_order",
    "ftmo_real", "place_order", "mt5_real_order", "broker_live_execution",
    "real_new_order", "live_new_order",
])
def test_unknown_and_real_actions_fail_closed(action):
    assert ComplianceEngine().check({**SAFE, "action": action}).allowed is False


@pytest.mark.parametrize("field,value", [
    ("mode", "LIVE"), ("mode", None), ("real_orders", "ALLOWED"),
    ("ftmo_real", "ALLOWED"), ("ftmo_real", None),
])
def test_safety_metadata_required(field, value):
    assert not ComplianceEngine().check({**SAFE, "action": "paper_feedback", field: value}).allowed


@pytest.mark.parametrize("event", [None, [], {}, {"action": None}, {"action": []}])
def test_invalid_event_fails_closed(event):
    assert not ComplianceEngine().check(event).allowed


def test_custom_allowlist_cannot_override_real_order_ban():
    engine = ComplianceEngine({"override": {"allowed_actions": ["real_order"], "blocked_actions": []}})
    assert not engine.check({**SAFE, "action": "real_order"}).allowed


def test_custom_allowlist_does_not_override_missing_paper_flags():
    engine = ComplianceEngine({"override": {"allowed_actions": ["paper_feedback"], "blocked_actions": []}})
    assert not engine.check({"action": "paper_feedback"}).allowed


def test_invalid_policy_fails_closed():
    assert not ComplianceEngine({"broken": {"allowed_actions": None}}).check({**SAFE, "action": "paper_feedback"}).allowed


def test_decision_to_dict():
    result = ComplianceEngine().check({**SAFE, "action": "paper_feedback"})
    assert result.to_dict()["allowed"] is True
