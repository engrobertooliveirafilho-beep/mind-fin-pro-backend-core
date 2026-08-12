from app.modules.usde_core.runtime_binding import bind_usde_runtime

def test_runtime_binding():
    r = bind_usde_runtime()

    assert r["status"] == "ONLINE"
    assert r["scientific_os"]["status"] == "ONLINE"
    assert r["scientific_os"]["module_count"] >= 27
