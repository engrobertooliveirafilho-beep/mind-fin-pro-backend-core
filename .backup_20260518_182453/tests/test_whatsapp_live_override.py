from app.api.whatsapp import eldora_primary_runtime_reply

def test_live_whatsapp_override_oi():
    assert "vamos resolver" in eldora_primary_runtime_reply("u","oi").lower()

def test_live_whatsapp_override_not_working():
    assert "handler do canal" in eldora_primary_runtime_reply("u","ainda nao conseguimos resolver?").lower()

def test_live_whatsapp_override_what_to_do():
    assert "runtime do whatsapp" in eldora_primary_runtime_reply("u","o que fazer?").lower()

def test_live_whatsapp_override_identity():
    assert "eldora" in eldora_primary_runtime_reply("u","quem eh vc?").lower()
