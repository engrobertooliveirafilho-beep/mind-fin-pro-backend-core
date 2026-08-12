from app.runtime.automotive_domain_guard import (
    is_automotive_aks_context,
    automotive_domain_override,
    suppress_agricultural_contamination,
)


def test_p19p5_detects_aks_followup_without_mercedes_repeat():
    assert is_automotive_aks_context("desligado entra marcha, ligado não entra")


def test_p19p5_overrides_agricultural_domain_to_automotive():
    out = automotive_domain_override(
        "desligado entra marcha, ligado não entra",
        {"intent": "diagnosis", "domain": "agricultural_equipment"}
    )
    assert out["domain"] == "automotive"
    assert out["automotive_context"] == "mercedes_classe_a_aks"


def test_p19p5_suppresses_agricultural_wrong_answer():
    out = suppress_agricultural_contamination(
        "desligado entra marcha, ligado não entra",
        "Parece problema no sistema de transmissão do seu equipamento agrícola."
    )
    assert "equipamento agrícola" not in out.lower()
    assert "aks" in out.lower() or "embreagem" in out.lower()
    assert "mercedes classe a" in out.lower()
