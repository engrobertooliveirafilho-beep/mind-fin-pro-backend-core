from app.eldora.intelligence.llm_live import select_model_by_cost, generate_llm_response

def test_llm_config_shape():
    cfg = select_model_by_cost()
    assert "provider" in cfg
    assert "max_tokens" in cfg

def test_llm_fallback_safe():
    out = generate_llm_response("teste", "")
    assert "answer" in out
    assert out["cost_controlled"] is True
