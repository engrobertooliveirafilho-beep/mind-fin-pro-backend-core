from app.api.whatsapp import eldora_primary_runtime_reply

def test_weather_request_safe():
    out = eldora_primary_runtime_reply("u","qual a previsão do tempo para amanhã em Jaguariuna?").lower()
    assert "clima real" in out or "api de previsão" in out

def test_typo_not_understood():
    out = eldora_primary_runtime_reply("u","nao entnedeu?").lower()
    assert "fallback" in out or "entendi" in out
