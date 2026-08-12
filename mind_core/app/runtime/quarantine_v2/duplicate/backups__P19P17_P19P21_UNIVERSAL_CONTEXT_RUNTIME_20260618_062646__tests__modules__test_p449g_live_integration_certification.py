from app.modules.usde_core.live_integration_certification import USDELiveIntegrationCertification

def test_live_integration_certification():
    r=USDELiveIntegrationCertification().certify()

    assert r["status"]=="CERTIFIED"
    assert "whatsapp" in r["channels"]
    assert "eldora_core" in r["channels"]
    assert "supabase" in r["channels"]
    assert "drive" in r["channels"]
