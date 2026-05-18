from app.api.whatsapp import eldora_primary_runtime_reply

def test_noisy_how_followup():
    out = eldora_primary_runtime_reply("u","como?4").lower()
    assert "camadas" in out
    assert "respostas curtas" in out
