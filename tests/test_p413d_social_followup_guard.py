from app.runtime.whatsapp_social_followup_guard import whatsapp_social_followup_guard, block_meta_reply

def test_social_how_are_you():
    assert "estou bem" in whatsapp_social_followup_guard("como vc ta?").lower()

def test_followup_no_meta():
    out = whatsapp_social_followup_guard("aprofunde")
    assert "execução contextual" not in out.lower()
    assert ("evidência" in out.lower()) or ("evidencia" in out.lower())

def test_block_meta_reply():
    assert block_meta_reply("Execução contextual: aprofundar a causa")
