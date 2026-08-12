from app.runtime.capability_identity.universal_capability_identity import (
    build_identity_map,
    resolve_capability,
)

def test_mind_os_44a_identity_map_shadow_only():
    identity = build_identity_map()

    assert identity["mode"] == "SHADOW_ONLY"
    assert identity["shadow_only"] is True
    assert identity["production_allowed"] is False
    assert identity["capability_count"] >= 5

def test_mind_os_44a_core_aliases_resolve():
    semantic_file = resolve_capability("app/api/eldora_semantic.py")
    semantic_module = resolve_capability("app.api.eldora_semantic")

    assert semantic_file["uid"] == semantic_module["uid"]
    assert semantic_file["production_allowed"] is False
    assert semantic_file["mode"] == "SHADOW_ONLY"

def test_mind_os_44a_all_records_have_uid():
    identity = build_identity_map()

    for cap in identity["capabilities"]:
        assert cap["uid"].startswith("CAP_")
        assert cap["mode"] == "SHADOW_ONLY"
        assert cap["production_allowed"] is False
        assert isinstance(cap["aliases"], list)
        assert isinstance(cap["sources"], list)
