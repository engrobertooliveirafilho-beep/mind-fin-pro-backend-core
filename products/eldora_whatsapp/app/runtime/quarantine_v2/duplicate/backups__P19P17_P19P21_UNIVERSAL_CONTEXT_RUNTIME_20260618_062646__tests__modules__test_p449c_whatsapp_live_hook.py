from app.api.whatsapp import p449c_usde_whatsapp_hook

def test_p449c_whatsapp_hook():
    r=p449c_usde_whatsapp_hook()

    assert "hypothesis" in r
    assert "experiment" in r
    assert "evidence" in r
    assert "decision" in r
