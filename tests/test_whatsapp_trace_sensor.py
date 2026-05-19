from app.runtime.whatsapp_trace_sensor import sanitize_final_output, assert_clean_output, leak_type
def test_sensor_blocks_neura_tutor():
    raw="Oi! Eu sou a NEURA, sua tutora cognitiva. Estou aqui para ajudar com suas dúvidas e estudos. Como posso te ajudar hoje?"
    out=sanitize_final_output("como vc chama?",raw)
    ok,hits=assert_clean_output(out)
    assert ok
    assert "NEURA" not in out
    assert "tutora" not in out.lower()
def test_leak_detector_finds_bad():
    assert leak_type("Eu sou a NEURA, sua tutora cognitiva")
