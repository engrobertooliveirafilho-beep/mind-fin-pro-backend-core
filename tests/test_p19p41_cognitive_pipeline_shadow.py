from app.runtime.cognitive_pipeline import (
    attach_p19p41_cognitive_context_shadow,
)

def test_pipeline_receives_context_shadow():

    ctx = {
        "cognitive_context": {
            "schema_version": "p19p39.v1"
        }
    }

    result = attach_p19p41_cognitive_context_shadow(ctx)

    shadow = result["p19p41_cognitive_pipeline_shadow"]

    assert shadow["program"] == "P19P41"
    assert shadow["mode"] == "SHADOW_ONLY"
    assert shadow["context_present"] is True
    assert shadow["runtime_mutation"] is False
    assert shadow["response_mutation"] is False

def test_pipeline_disabled_by_default():

    ctx = {}

    result = attach_p19p41_cognitive_context_shadow(ctx)

    shadow = result["p19p41_cognitive_pipeline_shadow"]

    assert shadow["enabled"] is False

def test_pipeline_feature_flag_enabled():

    ctx = {}

    result = attach_p19p41_cognitive_context_shadow(
        ctx,
        {
            "P19P41_COGNITIVE_CONTEXT_ENABLED": True
        }
    )

    shadow = result["p19p41_cognitive_pipeline_shadow"]

    assert shadow["enabled"] is True
