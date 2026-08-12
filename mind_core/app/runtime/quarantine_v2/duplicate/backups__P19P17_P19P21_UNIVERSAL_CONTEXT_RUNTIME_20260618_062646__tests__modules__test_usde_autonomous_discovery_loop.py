from app.modules.usde_core.autonomous_discovery_loop import AutonomousDiscoveryLoop

def test_autonomous_discovery_loop():
    r=AutonomousDiscoveryLoop().run_once(
        {"events":1000}
    )

    assert r["status"]=="COMPLETED"
    assert r["health"]["status"]=="HEALTHY"
