from app.runtime.conversation_recovery_engine import analyze_conversation_signal


def test_identity_intent_qual_seu_nome():
    result = analyze_conversation_signal("qual seu nome")
    assert result["intent"] == "identity"
    assert result["should_answer_directly"] is True
    assert result["confidence"] >= 0.9


def test_identity_intent_como_voce_chama():
    result = analyze_conversation_signal("como você chama?")
    assert result["intent"] == "identity"
    assert result["should_preserve_context"] is True


def test_capability_intent_o_que_voce_faz():
    result = analyze_conversation_signal("o que você faz?")
    assert result["intent"] == "capability"
    assert result["should_answer_directly"] is True


def test_acknowledgement_ok_not_fallback():
    result = analyze_conversation_signal("ok", last_topic="automatizar confinamento de boi")
    assert result["intent"] == "acknowledgement"
    assert result["should_preserve_context"] is True
    assert result["recovered_topic"] == "automatizar confinamento de boi"


def test_acknowledgement_legal_not_fallback():
    result = analyze_conversation_signal("legal", last_topic="matemática")
    assert result["intent"] == "acknowledgement"
    assert result["recovered_topic"] == "matemática"


def test_followup_como_faco_isso_recovers_topic():
    result = analyze_conversation_signal("como faço isso?", last_topic="automatizar confinamento de boi")
    assert result["intent"] == "context_followup"
    assert result["should_preserve_context"] is True
    assert result["recovered_topic"] == "automatizar confinamento de boi"


def test_followup_explique_melhor_recovers_topic():
    result = analyze_conversation_signal("explique melhor", last_topic="função quadrática")
    assert result["intent"] == "context_followup"
    assert result["recovered_topic"] == "função quadrática"


def test_context_recovery_short_contextual_message():
    result = analyze_conversation_signal("e agora?", last_topic="criar campanha")
    assert result["intent"] in ("context_followup", "context_recovery")
    assert result["recovered_topic"] == "criar campanha"


def test_unknown_preserves_topic_without_direct_answer():
    result = analyze_conversation_signal("mensagem completamente nova sem padrão", last_topic="academia")
    assert result["intent"] == "unknown"
    assert result["should_answer_directly"] is False
    assert result["recovered_topic"] == "academia"
