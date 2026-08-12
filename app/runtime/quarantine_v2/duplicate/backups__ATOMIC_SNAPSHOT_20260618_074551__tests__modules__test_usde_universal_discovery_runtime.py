from app.modules.usde_core.universal_discovery_runtime import UniversalDiscoveryRuntime

def test_discovery_runtime():
    r=UniversalDiscoveryRuntime().discover({
        "temporal":True,
        "graph":True,
        "symbolic":True
    })

    assert r["count"] > 0

def test_discovery_runtime_automl():
    r=UniversalDiscoveryRuntime().discover({
        "automl":True
    })

    assert "AutoMLEngine" in r["selected_engines"]
