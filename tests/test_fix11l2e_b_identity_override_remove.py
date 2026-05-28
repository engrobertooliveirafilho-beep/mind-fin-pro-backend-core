def test_identity_question_delegates_to_real_handler():
    from app.api.whatsapp import live_whatsapp_override
    out = live_whatsapp_override("Quem é vc?")
    assert out is None
