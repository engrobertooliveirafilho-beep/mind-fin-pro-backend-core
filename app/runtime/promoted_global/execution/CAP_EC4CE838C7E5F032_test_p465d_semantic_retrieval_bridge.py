from app.runtime.cognitive_pipeline import run_cognitive_pipeline


def test_p465d_semantic_retrieval_bridge_does_not_break_pipeline():
    out = run_cognitive_pipeline(
        "p465d_test",
        "Use retrieval da base do Drive para responder: qual é o estado atual da Eldora?",
    )

    assert isinstance(out, dict)
    assert "answer" in out
    assert "intent" in out


def test_p465d_pipeline_still_answers_normal_message():
    out = run_cognitive_pipeline("p465d_test_normal", "quero criar plano estratégico da Eldora")

    assert isinstance(out, dict)
    assert "answer" in out
    assert len(str(out["answer"])) > 20
