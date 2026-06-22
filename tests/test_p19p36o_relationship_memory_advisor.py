from pathlib import Path

from app.companionship.relationship_memory_store import (
    attach_relationship_memory_advisor_shadow,
    build_relationship_memory_advisor,
    get_relationship_memory,
    update_relationship_memory_shadow,
)


def test_p19p36o_c_advisor_scores_relationship_context(tmp_path):
    path = tmp_path / "relationship_memory.json"
    sender = "u1"

    update_relationship_memory_shadow(sender, "quero emagrecer", path=path)
    update_relationship_memory_shadow(sender, "tenho dor no joelho", path=path)

    advisor = build_relationship_memory_advisor(sender, "quais exercícios?", path=path)

    assert advisor["relationship_score"] > 0
    assert advisor["relationship_confidence"] in {"MEDIUM", "HIGH"}
    assert "emagrecer" in advisor["recommended_relationship_context"]


def test_p19p36o_c_advisor_scores_ftmo_context(tmp_path):
    path = tmp_path / "relationship_memory.json"
    sender = "u2"

    update_relationship_memory_shadow(sender, "estou estudando para FTMO", path=path)

    advisor = build_relationship_memory_advisor(sender, "como melhorar na FTMO?", path=path)

    assert advisor["relationship_score"] > 0
    assert "FTMO" in advisor["recommended_relationship_context"] or "aprovação FTMO" in advisor["recommended_relationship_context"]


def test_p19p36o_c_advisor_returns_low_when_no_match(tmp_path):
    path = tmp_path / "relationship_memory.json"
    sender = "u3"

    update_relationship_memory_shadow(sender, "quero emagrecer", path=path)

    advisor = build_relationship_memory_advisor(sender, "como abrir empresa de software?", path=path)

    assert advisor["relationship_score"] == 0.0
    assert advisor["relationship_confidence"] == "LOW"
    assert advisor["recommended_relationship_context"] == []


def test_p19p36o_c_attach_shadow_adds_context(tmp_path, monkeypatch):
    sender = "u4"
    update_relationship_memory_shadow(sender, "quero emagrecer")

    ctx = attach_relationship_memory_advisor_shadow({}, sender=sender, text="quais exercícios?")

    assert "p19p36o_relationship_memory_advisor_shadow" in ctx
    assert ctx["p19p36o_relationship_memory_advisor_shadow"]["mode"] == "SHADOW_ONLY"
