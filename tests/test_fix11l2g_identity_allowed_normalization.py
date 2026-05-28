from app.runtime.whatsapp_final_output_guard import identity_allowed

def test_identity_allowed_short_vc():
    assert identity_allowed("quem é vc?")
    assert identity_allowed("quem e vc?")
    assert identity_allowed("quem é você?")
