from app.eldora.core.live_connector_fabric import register_connector
from app.eldora.core.cross_platform_execution_bus import route_execution
from app.eldora.core.infrastructure_event_engine import infrastructure_event

def test_connector():
    r=register_connector("gmail","automation")
    assert r["status"]=="ok"

def test_execution_bus():
    r=route_execution("gmail","crm","lead_sync")
    assert r["status"]=="ok"

def test_infrastructure_event():
    r=infrastructure_event("render","runtime_signal")
    assert r["status"]=="ok"
