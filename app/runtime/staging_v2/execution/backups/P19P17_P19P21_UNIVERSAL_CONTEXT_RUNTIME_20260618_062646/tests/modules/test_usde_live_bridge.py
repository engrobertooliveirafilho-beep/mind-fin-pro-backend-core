from app.modules.usde_core.live_bridge import USDELiveBridge

def test_live_bridge_status():
    r=USDELiveBridge().status()
    assert r["status"]=="ONLINE"

def test_live_bridge_observe():
    r=USDELiveBridge().observe("whatsapp",{"type":"message"})
    assert "hypothesis" in r
    assert "experiment" in r
    assert "evidence" in r
    assert "decision" in r
