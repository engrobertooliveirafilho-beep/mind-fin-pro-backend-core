from app.p142_nelogica_api_connector.engine import env_status, connector_status, run

def test_p142_env_status_has_required_keys():
    s=env_status()
    assert "NELOGICA_BASE_URL" in s
    assert "NELOGICA_API_KEY" in s

def test_p142_blocks_orders():
    s=connector_status()
    assert s["order_routing_enabled"] is False
    assert s["real_orders"]=="FORBIDDEN"

def test_p142_manifest():
    m=run()
    assert m["STATUS"]=="P14.2_NELOGICA_API_CONNECTOR_FOUNDATION_IMPLEMENTED"
    assert m["EXPORT_READY"] is True
