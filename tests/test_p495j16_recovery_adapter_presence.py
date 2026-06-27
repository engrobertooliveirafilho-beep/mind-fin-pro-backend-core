from app.api import whatsapp


def test_p495j16_recovery_adapter_exists():
    assert hasattr(whatsapp, "_p495_recovery_signal")


def test_p495j16_recovery_adapter_identity():
    result = whatsapp._p495_recovery_signal("qual seu nome", last_topic="teste")
    assert result["intent"] == "identity"
    assert result["should_answer_directly"] is True


def test_p495j16_recovery_adapter_followup():
    result = whatsapp._p495_recovery_signal("como faço isso?", last_topic="automatizar confinamento de boi")
    assert result["intent"] == "context_followup"
    assert result["recovered_topic"] == "automatizar confinamento de boi"
