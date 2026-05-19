from app.humanization.universal_recovery_runtime import universal_recovery_answer, contains_identity_fallback

BAD="Eu sou a Eldora, a camada conversacional do MIND. Minha função é entender seu contexto, lembrar o que importa e te ajudar sem você precisar reexplicar tudo."

def assert_no_identity(prompt):
    out=universal_recovery_answer(prompt,BAD)
    assert "sou a eldora" not in out.lower()
    assert "camada conversacional" not in out.lower()
    assert "minha função" not in out.lower()
    return out

def test_oi_no_identity():
    assert "Oi" in assert_no_identity("oi")

def test_diesel_no_identity():
    out=assert_no_identity("qual diferença diesel?")
    assert "diesel" in out.lower()

def test_carros_no_identity():
    out=assert_no_identity("me explica carros")
    assert "carro" in out.lower()

def test_sentiu_diferenca_no_identity():
    out=assert_no_identity("sentiu diferença?")
    assert "diferença" in out.lower() or "fallback" in out.lower()

def test_porque_no_identity():
    out=assert_no_identity("porque?")
    assert "porque" in out.lower() or "contexto" in out.lower()

def test_boa_tarde_no_identity():
    assert "Roberto" in assert_no_identity("boa tarde")

def test_detects_identity():
    assert contains_identity_fallback(BAD) is True
