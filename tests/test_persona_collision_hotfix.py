from pathlib import Path
from app.runtime.visible_response_layer import build_visible_response

def test_no_neura_tutor_literal_in_personality_layer():
    txt = Path("app/dialogue/personality_layer.py").read_text(encoding="utf-8")
    assert "Eu sou a NEURA, sua tutora cognitiva" not in txt
    assert "tutora cognitiva" not in txt.lower()

def test_identity_short_has_eldora_mind():
    out = build_visible_response("qual seu nome?")
    assert "Eldora" in out
    assert "MIND" in out
    assert "Estado atual" not in out
