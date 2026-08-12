from app.p18_conversational_execution.failure_fixes import fix_real_whatsapp_failure

def test_p19a_3_fluidez_no_context_contamination():
    result = fix_real_whatsapp_failure("detalhe melhor", previous_topic="fluidez")
    assert result["status"] == "PASS"
    assert "preço" not in result["answer"].lower()
    assert "estriado" not in result["answer"].lower()
    assert result["context_guard"]["contaminated"] is False

def test_p19a_3_cac_intent_preserved():
    result = fix_real_whatsapp_failure("quero validar CAC")
    assert result["status"] == "PASS"
    assert "CAC" in result["answer"] or "cac" in result["answer"].lower()

def test_p19a_3_sleep_fallback_correct():
    result = fix_real_whatsapp_failure("nao dormi bem hoje")
    assert result["status"] == "PASS"
    assert "sono" in result["answer"].lower()

def test_p19a_3_step_by_step_keeps_topic():
    result = fix_real_whatsapp_failure("passo a passo", previous_topic="fluidez")
    assert result["status"] == "PASS"
    assert "contexto" in result["answer"].lower()
