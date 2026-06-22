from app.companionship.live_cognition_gated import (
    REQUIRED_LAYERS,
    attach_live_cognition_shadow,
    build_live_cognition_decision,
    live_cognition_enabled,
)


def test_p19p37f_default_off(monkeypatch):
    monkeypatch.delenv("P19P37_LIVE_COGNITION_ENABLED", raising=False)

    out = build_live_cognition_decision({})

    assert live_cognition_enabled() is False
    assert out["enabled"] is False
    assert out["live_allowed"] is False
    assert out["mode"] == "SHADOW_ONLY"
    assert out["response_impact"] == "NONE"
    assert "feature_flag_off" in out["reasons"]


def test_p19p37f_requires_all_layers_even_when_enabled(monkeypatch):
    monkeypatch.setenv("P19P37_LIVE_COGNITION_ENABLED", "true")

    out = build_live_cognition_decision({
        "p19p37a_digital_twin_real_shadow": {},
    })

    assert out["enabled"] is True
    assert out["live_allowed"] is False
    assert "missing_required_layers" in out["reasons"]


def test_p19p37f_allows_live_when_flag_and_layers_present(monkeypatch):
    monkeypatch.setenv("P19P37_LIVE_COGNITION_ENABLED", "true")

    ctx = {k: {} for k in REQUIRED_LAYERS}

    out = build_live_cognition_decision(ctx)

    assert out["enabled"] is True
    assert out["live_allowed"] is True
    assert out["mode"] == "LIVE_GATED"
    assert out["response_impact"] == "ALLOWED_BY_FEATURE_FLAG"


def test_p19p37f_attach_shadow():
    ctx = attach_live_cognition_shadow({})

    assert "p19p37f_live_cognition_decision" in ctx
    assert ctx["p19p37f_live_cognition_decision"]["version"] == "P19P37F_LIVE_COGNITION_GATED"
