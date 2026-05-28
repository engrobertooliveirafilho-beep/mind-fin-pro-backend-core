def test_primary_identity_precedence_before_override():
    from app.api.whatsapp import eldora_primary_runtime_reply
    out = eldora_primary_runtime_reply("test_sender", "Quem é vc?")
    assert out == "Sou a Eldora 🙂"
