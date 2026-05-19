from app.runtime.whatsapp_final_output_guard import guard_whatsapp_final_answer, has_identity_leak

BAD = "Eu sou a Eldora, a camada conversacional do MIND. Minha função é entender seu contexto, lembrar o que importa e te ajudar sem você precisar reexplicar tudo."

def test_blocks_identity_leak_for_implantations():
    out = guard_whatsapp_final_answer("vou fazer mais algumas implatações para te ajudar", BAD)
    assert "sou a eldora" not in out.lower()
    assert "implant" in out.lower() or "camada" in out.lower()

def test_blocks_identity_leak_for_diesel():
    out = guard_whatsapp_final_answer("qual a diferença do motor a diesel?", BAD)
    assert "sou a eldora" not in out.lower()
    assert "diesel" in out.lower()
    assert "compressão" in out.lower() or "compressao" in out.lower()

def test_blocks_identity_leak_for_cars():
    out = guard_whatsapp_final_answer("me explica sobre carros", BAD)
    assert "sou a eldora" not in out.lower()
    assert "carros" in out.lower() or "motor" in out.lower()

def test_blocks_identity_leak_for_felt_difference():
    out = guard_whatsapp_final_answer("sentiu diferença?", BAD)
    assert "sou a eldora" not in out.lower()
    assert "fallback" in out.lower() or "diferença" in out.lower() or "diferenca" in out.lower()

def test_allows_identity_when_explicit():
    out = guard_whatsapp_final_answer("quem é você?", BAD)
    assert "sou a eldora" in out.lower()

def test_detects_identity_leak():
    assert has_identity_leak(BAD) is True
