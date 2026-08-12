from app.runtime.final_authority_selector import select_final_authority_candidate


def test_p495g_selects_non_generic_safe_candidate():
    result = select_final_authority_candidate([
        {
            "source": "legacy_context_signal",
            "text": "{'type': 'context_signal'}",
            "safe": True,
            "send_to_user": True,
        },
        {
            "source": "cognitive_pipeline",
            "text": "Resposta humana útil com direção clara para o próximo passo.",
            "safe": True,
            "send_to_user": True,
        },
    ])

    assert result["ok"] is True
    assert result["selected"]["source"] == "cognitive_pipeline"


def test_p495g_does_not_force_send_to_user():
    result = select_final_authority_candidate([
        {
            "source": "universal_authority_renderer",
            "text": "Intenção detectada: assist. Plano interno seguro.",
            "safe": True,
            "send_to_user": False,
        }
    ])

    assert result["ok"] is True
    assert result["send_to_user"] is False


def test_p495g_rejects_invalid_input():
    result = select_final_authority_candidate(None)
    assert result["ok"] is False
