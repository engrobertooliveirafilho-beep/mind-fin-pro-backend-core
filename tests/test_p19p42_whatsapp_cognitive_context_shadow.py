from app.api.whatsapp import (
    attach_p19p42_whatsapp_cognitive_context_shadow,
)


def test_p19p42_whatsapp_receives_cognitive_context_read_only_shadow():
    ctx = {
        "cognitive_context": {
            "schema_version": "p19p39.v1",
            "mode": "SHADOW_ONLY",
        },
        "outbound_text": "texto original",
    }

    result = attach_p19p42_whatsapp_cognitive_context_shadow(ctx)

    shadow = result["p19p42_whatsapp_cognitive_context_shadow"]

    assert result["outbound_text"] == "texto original"
    assert shadow["program"] == "P19P42"
    assert shadow["mode"] == "SHADOW_ONLY"
    assert shadow["read_only"] is True
    assert shadow["context_present"] is True
    assert shadow["runtime"] == "whatsapp"
    assert shadow["runtime_mutation"] is False
    assert shadow["response_mutation"] is False
    assert shadow["outbound_text_mutation"] is False
    assert shadow["rollbackable"] is True
    assert shadow["canary_ready"] is True


def test_p19p42_whatsapp_disabled_by_default():
    result = attach_p19p42_whatsapp_cognitive_context_shadow({})

    shadow = result["p19p42_whatsapp_cognitive_context_shadow"]

    assert shadow["enabled"] is False


def test_p19p42_whatsapp_feature_flag_enabled():
    result = attach_p19p42_whatsapp_cognitive_context_shadow(
        {},
        {
            "P19P42_WHATSAPP_COGNITIVE_CONTEXT_ENABLED": True,
        },
    )

    shadow = result["p19p42_whatsapp_cognitive_context_shadow"]

    assert shadow["enabled"] is True


def test_p19p42_whatsapp_does_not_mutate_original_context():
    ctx = {
        "cognitive_context": {
            "schema_version": "p19p39.v1",
        }
    }

    result = attach_p19p42_whatsapp_cognitive_context_shadow(ctx)

    assert result is not ctx
    assert "p19p42_whatsapp_cognitive_context_shadow" not in ctx
    assert "p19p42_whatsapp_cognitive_context_shadow" in result
