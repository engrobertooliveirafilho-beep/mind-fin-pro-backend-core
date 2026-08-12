import os

from app.runtime.assisted_bypass_runtime import build_universal_assisted_context
from app.runtime.universal_authority_renderer import render_universal_authority_candidate


def test_p495b_renderer_from_mind_os_context():
    os.environ["MIND_ENABLE_MINDOS_ASSISTED_BYPASS"] = "1"
    ctx = build_universal_assisted_context("marketing para vender consultoria")
    rendered = render_universal_authority_candidate(ctx)

    assert rendered["ok"] is True
    assert rendered["send_to_user"] is False
    assert rendered["execution_allowed"] is False
    assert rendered["production_allowed"] is False
    assert rendered["shadow_only"] is True
    assert rendered["quality"]["safe"] is True
    assert "Intenção detectada" in rendered["text"]
    assert "Execução direta continua bloqueada" in rendered["text"]


def test_p495b_renderer_rejects_invalid_context():
    rendered = render_universal_authority_candidate({})
    assert rendered["ok"] is False
    assert rendered["send_to_user"] is False
