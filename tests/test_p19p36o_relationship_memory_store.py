from pathlib import Path

from app.companionship.relationship_memory_store import (
    extract_relationship_candidates,
    get_relationship_memory,
    relationship_memory_enabled,
    update_relationship_memory_shadow,
)


def test_p19p36o_feature_flag_default_off(monkeypatch):
    monkeypatch.delenv("P19P36O_RELATIONSHIP_MEMORY_ENABLED", raising=False)
    assert relationship_memory_enabled() is False


def test_p19p36o_extracts_goal_emagrecer():
    out = extract_relationship_candidates("quero emagrecer")
    assert "emagrecer" in out["goals"]


def test_p19p36o_extracts_fact_dor_no_joelho():
    out = extract_relationship_candidates("tenho dor no joelho")
    assert "dor joelho" in out["facts"]


def test_p19p36o_extracts_ftmo_project_and_goal():
    out = extract_relationship_candidates("estou estudando para FTMO")
    assert "FTMO" in out["projects"]
    assert "aprovação FTMO" in out["goals"]


def test_p19p36o_persists_relationship_memory(tmp_path):
    path = tmp_path / "relationship_memory.json"
    sender = "5511999999999"

    update_relationship_memory_shadow(sender, "quero emagrecer", path=path)
    update_relationship_memory_shadow(sender, "tenho dor no joelho", path=path)
    update_relationship_memory_shadow(sender, "estou estudando para FTMO", path=path)

    profile = get_relationship_memory(sender, path=path)

    assert "emagrecer" in profile["goals"]
    assert "aprovação FTMO" in profile["goals"]
    assert "dor joelho" in profile["facts"]
    assert "FTMO" in profile["projects"]


def test_p19p36o_deduplicates_values(tmp_path):
    path = tmp_path / "relationship_memory.json"
    sender = "abc"

    update_relationship_memory_shadow(sender, "quero emagrecer", path=path)
    update_relationship_memory_shadow(sender, "quero emagrecer", path=path)

    profile = get_relationship_memory(sender, path=path)

    assert profile["goals"].count("emagrecer") == 1
