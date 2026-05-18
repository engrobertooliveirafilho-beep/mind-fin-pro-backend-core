from app.eldora.core.live_browser_agents import activate_browser_agent
from app.eldora.core.autonomous_digital_presence import digital_presence
from app.eldora.core.internet_awareness_engine import internet_awareness

def test_browser_agent():
    r=activate_browser_agent("agent_web","market_scan")
    assert r["status"]=="ok"

def test_digital_presence():
    r=digital_presence("eldora","whatsapp")
    assert r["status"]=="ok"

def test_internet_awareness():
    r=internet_awareness("twitter","trend_signal")
    assert r["status"]=="ok"
