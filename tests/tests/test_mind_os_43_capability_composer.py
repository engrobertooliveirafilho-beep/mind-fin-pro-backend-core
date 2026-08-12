from app.runtime.capability_governance.capability_composer import compose_capabilities


def test_mind_os_43_composer_shadow_only():
    result = compose_capabilities("como automatizar confinamento de boi")

    assert result["mode"] == "SHADOW_ONLY"
    assert result["shadow_only"] is True
    assert result["execution_allowed"] is False
    assert result["final_authority_required"] is True
    assert result["chain_length"] >= 3

    for step in result["capability_chain"]:
        assert step["mode"] == "SHADOW_ONLY"
        assert step["production_allowed"] is False
        assert step["direct_user_response_allowed"] is False


def test_mind_os_43_composer_intent_variation():
    strategy = compose_capabilities("crie estratégia de marketing para eldora")
    diagnostic = compose_capabilities("validar runtime trader FTMO paper only")
    proceed = compose_capabilities("prossiga")

    assert strategy["intent"] == "generate_strategy_or_content"
    assert diagnostic["intent"] == "diagnose_or_validate"
    assert proceed["intent"] == "continue_current_mission"

    assert strategy["capability_chain"] != diagnostic["capability_chain"]
