from app.modules.usde_core.scientific_os import ScientificOS

def test_scientific_os_boot():
    r=ScientificOS().boot()

    assert r["status"]=="ONLINE"
    assert r["module_count"]>20

def test_scientific_os_health():
    r=ScientificOS().health()

    assert r["status"]=="HEALTHY"
