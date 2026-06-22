from app.companionship.emotional_continuity_real import detect_emotional_signal, update_emotional_continuity

def test_detects_signal_without_diagnosis():
    out = detect_emotional_signal("travou e estou frustrado")
    assert "friction" in out["signals"]
    assert out["diagnosis"] is None

def test_persists_signal(tmp_path):
    out = update_emotional_continuity("u", "perfeito passou", path=tmp_path/"e.json")
    assert out["profile"]["recent_signals"]
