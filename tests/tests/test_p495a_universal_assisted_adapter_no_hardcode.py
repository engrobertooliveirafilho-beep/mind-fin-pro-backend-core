import os

from app.runtime.assisted_bypass_runtime import (
    assisted_bypass_enabled,
    build_assisted_bypass_reply,
    build_universal_assisted_context,
)


def test_p495a_default_off():
    os.environ["MIND_ENABLE_MINDOS_ASSISTED_BYPASS"] = "0"
    assert assisted_bypass_enabled() is False
    assert build_assisted_bypass_reply("marketing para vender consultoria") == ""


def test_p495a_enabled_does_not_return_hardcoded_answer():
    os.environ["MIND_ENABLE_MINDOS_ASSISTED_BYPASS"] = "1"
    assert assisted_bypass_enabled() is True
    assert build_assisted_bypass_reply("marketing para vender consultoria") == ""
    assert build_assisted_bypass_reply("quero estudar matemática") == ""
    assert build_assisted_bypass_reply("Mercedes não entra ré") == ""


def test_p495a_universal_context_builds_shadow_candidate():
    os.environ["MIND_ENABLE_MINDOS_ASSISTED_BYPASS"] = "1"
    ctx = build_universal_assisted_context("marketing para vender consultoria")
    assert ctx["enabled"] is True
    assert ctx["execution_allowed"] is False
    assert ctx["production_allowed"] is False
    assert ctx["shadow_only"] is True
    assert ctx["ok"] is True
    assert "MIND-OS_ASSISTED_CANDIDATE" in ctx["candidate_text"]
    assert ctx["capability_chain"] is not None
    assert ctx["knowledge_context"] is not None
    assert ctx["execution_graph"] is not None
