from app.api.whatsapp import eldora_primary_runtime_reply, twiml

def test_primary_whatsapp_runtime():
    out = eldora_primary_runtime_reply("whatsapp:+5511999999999", "prosseguir evolução do MIND")
    assert "Diagnóstico" in out
    assert "Estratégia" in out
    assert "Execução" in out
    assert "Auditoria" in out

def test_twiml():
    xml = twiml("ok")
    assert "<Response>" in xml
    assert "<Message>ok</Message>" in xml
