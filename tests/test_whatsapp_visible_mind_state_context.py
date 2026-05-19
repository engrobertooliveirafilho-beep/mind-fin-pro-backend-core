from app.api.whatsapp import eldora_primary_runtime_reply

def test_whatsapp_visible_mind_state_context():
    out=eldora_primary_runtime_reply("whatsapp:+55","resuma o estado atual")
    assert "194/194" in out
    assert "Twilio" in out
    assert "Webhook" in out or "webhook" in out
    assert "avatar" not in out.lower()
    assert "loira" not in out.lower()
