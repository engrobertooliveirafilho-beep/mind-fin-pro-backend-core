import os

from app.companionship.safe_recovery_adapter import (
    build_memory_fusion_live_context,
    record_p19p36n_memory_fusion_telemetry,
)


def test_p19p36n_default_off_shadow_only(monkeypatch):
    monkeypatch.delenv("P19P36N_MEMORY_FUSION_ENABLED", raising=False)

    ctx = {
        "p19p36m_memory_fusion_advisor_shadow": {
            "should_use_memory": True,
            "memory_score": 0.88,
            "recommended_memories": ["quero emagrecer", "tenho dor no joelho"],
        }
    }

    out = build_memory_fusion_live_context(ctx)
    live = out["p19p36n_memory_fusion_live_context"]

    assert live["enabled"] is False
    assert live["live_allowed"] is False
    assert live["mode"] == "SHADOW_ONLY"


def test_p19p36n_enabled_allows_positive_advisor(monkeypatch):
    monkeypatch.setenv("P19P36N_MEMORY_FUSION_ENABLED", "true")

    ctx = {
        "p19p36m_memory_fusion_advisor_shadow": {
            "should_use_memory": True,
            "memory_score": 0.88,
            "recommended_memories": ["quero emagrecer", "tenho dor no joelho"],
        }
    }

    out = build_memory_fusion_live_context(ctx)
    live = out["p19p36n_memory_fusion_live_context"]

    assert live["enabled"] is True
    assert live["live_allowed"] is True
    assert live["mode"] == "LIVE_GATED"


def test_p19p36n_enabled_blocks_zero_score(monkeypatch):
    monkeypatch.setenv("P19P36N_MEMORY_FUSION_ENABLED", "true")

    ctx = {
        "p19p36m_memory_fusion_advisor_shadow": {
            "should_use_memory": False,
            "memory_score": 0.0,
            "recommended_memories": [],
        }
    }

    out = build_memory_fusion_live_context(ctx)
    live = out["p19p36n_memory_fusion_live_context"]

    assert live["enabled"] is True
    assert live["live_allowed"] is False
    assert live["mode"] == "SHADOW_ONLY"


def test_p19p36n_telemetry_does_not_crash(tmp_path):
    ctx = {
        "p19p36n_memory_fusion_live_context": {
            "enabled": True,
            "live_allowed": True,
            "mode": "LIVE_GATED",
            "recommended_memories": ["x"],
        },
        "p19p36m_memory_fusion_advisor_shadow": {
            "memory_score": 0.9,
            "should_use_memory": True,
        },
    }

    record_p19p36n_memory_fusion_telemetry(
        sender="test",
        text="quais exercícios?",
        ctx=ctx,
        reply_before="antes",
        reply_after="depois",
    )
