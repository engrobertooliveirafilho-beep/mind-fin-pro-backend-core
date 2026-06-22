import os

from app.companionship.safe_recovery_adapter import collect_recovered_context


def test_p19p36o_shadow_wiring_collects_relationship_memory(monkeypatch, tmp_path):
    monkeypatch.setenv("P19P36O_RELATIONSHIP_MEMORY_ENABLED", "false")

    ctx = collect_recovered_context(
        sender="test_p19p36o_b",
        text="quero emagrecer",
        base_ctx={"active_domain": "fitness", "active_subject": "treino"}
    )

    shadow = ctx.get("p19p36o_relationship_memory_shadow", {})

    assert shadow
    assert shadow["mode"] == "SHADOW_ONLY"
    assert shadow["enabled"] is False
    assert "emagrecer" in shadow["profile"]["goals"]


def test_p19p36o_shadow_wiring_does_not_require_feature_flag(monkeypatch):
    monkeypatch.delenv("P19P36O_RELATIONSHIP_MEMORY_ENABLED", raising=False)

    ctx = collect_recovered_context(
        sender="test_p19p36o_b_default",
        text="tenho dor no joelho",
        base_ctx={"active_domain": "fitness", "active_subject": "joelho"}
    )

    shadow = ctx.get("p19p36o_relationship_memory_shadow", {})

    assert shadow
    assert shadow["mode"] == "SHADOW_ONLY"
    assert shadow["enabled"] is False
    assert "dor joelho" in shadow["profile"]["facts"]


def test_p19p36o_shadow_wiring_preserves_existing_memory_fusion(monkeypatch):
    ctx = collect_recovered_context(
        sender="test_p19p36o_b_preserve",
        text="estou estudando para FTMO",
        base_ctx={"active_domain": "trader", "active_subject": "FTMO"}
    )

    assert "p19p36k_memory_shadow" in ctx
    assert "p19p36l_memory_fusion_shadow" in ctx
    assert "p19p36m_memory_fusion_advisor_shadow" in ctx
    assert "p19p36n_memory_fusion_live_context" not in ctx or isinstance(ctx.get("p19p36n_memory_fusion_live_context"), dict)
    assert "p19p36o_relationship_memory_shadow" in ctx
