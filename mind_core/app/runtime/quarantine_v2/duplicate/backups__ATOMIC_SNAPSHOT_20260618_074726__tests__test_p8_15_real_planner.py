from app.p8_shadow.real_planner import generate_hierarchical_plan

def test_p8_15_real_planner_generates_hierarchy():
    result = generate_hierarchical_plan({"goal": "deploy controlled feature"})
    assert result["capability"] == "HIERARCHICAL_PLANNING"
    assert result["mode"] == "SHADOW"
    assert result["depth"] >= 3
    assert result["step_count"] >= 5
    assert len(result["plan"]) >= 5
    assert "execution_tree" in result
    assert result["runtime_modified"] is False
    assert result["runtime_authority_preserved"] is True

def test_p8_15_real_planner_steps_have_audit_fields():
    result = generate_hierarchical_plan({"goal": "audit rollout"})
    step = result["plan"][0]
    assert "objective" in step
    assert "depends_on" in step
    assert "risk" in step
    assert "validation" in step
