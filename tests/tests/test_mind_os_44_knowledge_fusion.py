from app.runtime.knowledge_fusion.knowledge_fusion_engine import fuse_knowledge

def test_mind_os_44_fusion_shadow_only():
    result = fuse_knowledge("como automatizar confinamento de boi")

    assert result["mode"] == "SHADOW_ONLY"
    assert result["shadow_only"] is True
    assert result["execution_allowed"] is False
    assert result["production_allowed"] is False
    assert result["final_authority_required"] is True
    assert result["chain_length"] >= 3

def test_mind_os_44_fusion_sources_present():
    result = fuse_knowledge("validar runtime trader FTMO paper only")

    for source in [
        "shadow_registry",
        "capability_descriptors",
        "semantic_contracts",
        "capability_graph",
        "capability_abstraction",
    ]:
        assert source in result["source_summary"]

    assert len(result["fused_capability_chain"]) == result["chain_length"]

def test_mind_os_44_fused_steps_have_evidence_map():
    result = fuse_knowledge("crie estratégia de marketing para eldora")

    for step in result["fused_capability_chain"]:
        assert step["mode"] == "SHADOW_ONLY"
        assert step["production_allowed"] is False
        assert step["direct_user_response_allowed"] is False
        assert step["fusion_status"] == "FUSED_SHADOW_EVIDENCE"
        assert "knowledge_evidence" in step
        assert isinstance(step["knowledge_evidence"], dict)
