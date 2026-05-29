from app.api.whatsapp import eldora_primary_runtime_reply

def test_deepen():
    out=eldora_primary_runtime_reply("u","aprofunde").lower()
    assert ("causa aberta" in out) or ("próximo passo" in out) or ("proximo passo" in out)
