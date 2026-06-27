from app.runtime.context_signal_candidate_normalizer import (
    build_context_signal_candidate,
    candidate_to_legacy_response,
)


def test_p495j3_candidate_preserves_legacy_response():
    legacy = "Oi! Eu sou a Eldora."
    candidate = build_context_signal_candidate(
        source="greeting",
        response=legacy,
        priority=100,
        confidence=1.0,
        metadata={"mission": "P4.95J3"},
    )

    assert candidate.source == "greeting"
    assert candidate.response == legacy
    assert candidate.priority == 100
    assert candidate.confidence == 1.0
    assert candidate.send_to_user is False
    assert candidate.shadow_only is True
    assert candidate.metadata["mission"] == "P4.95J3"
    assert candidate_to_legacy_response(candidate) == legacy
