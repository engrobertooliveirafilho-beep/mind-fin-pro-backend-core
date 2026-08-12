from app.modules.usde_core.full_runtime_certification import FullRuntimeCertification

def test_full_runtime_certification():
    r=FullRuntimeCertification().certify()

    assert r["status"]=="CERTIFIED"
    assert r["boot"]["status"]=="ONLINE"
    assert r["health"]["status"]=="HEALTHY"
    assert r["loop"]["status"]=="COMPLETED"
