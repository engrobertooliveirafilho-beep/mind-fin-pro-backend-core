from app.p8_shadow.planner_consumption_contract import (
    produce_consumable_planner_artifact,
    validate_planner_consumption_contract,
)

def test_p8_23_consumable_artifact_valid():
    result = produce_consumable_planner_artifact({"goal": "contract validation"})
    assert result["status"] == "PASS"
    assert result["consumption_allowed"] is True
    assert result["runtime_modified"] is False
    assert result["response_modified"] is False
    assert result["active_mode_enabled"] is False
    assert result["runtime_authority_preserved"] is True

def test_p8_23_contract_rejects_missing_fields():
    result = validate_planner_consumption_contract({"plan": []})
    assert result["status"] == "FAIL"
    assert result["valid"] is False
    assert len(result["missing_fields"]) > 0
