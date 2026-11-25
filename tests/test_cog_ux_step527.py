from app.cog_ux import CognitiveSafetySurface


def test_step527_low_uncertainty_sets_high_confidence_badge():
    surf = CognitiveSafetySurface()
    r = surf.render_response("ok", uncertainty=0.1)
    assert r["message"] == "ok"
    assert r["uncertainty_badge"] == "alta_confiança"
    assert 0.0 <= r["uncertainty_score"] <= 1.0


def test_step527_high_uncertainty_sets_high_uncertainty_badge_and_keeps_warnings():
    surf = CognitiveSafetySurface()
    r = surf.render_response(
        "cuidado",
        uncertainty=0.9,
        warnings=["modelo não treinado para este cenário"],
    )
    assert r["uncertainty_badge"] == "alta_incerteza"
    assert "modelo não treinado para este cenário" in r["warnings"]

