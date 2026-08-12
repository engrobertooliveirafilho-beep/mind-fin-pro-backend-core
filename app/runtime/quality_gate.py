def score_response(answer, intent, persona, memory):

    text = str(answer or "").strip()
    low = text.lower()

    bad_markers = [
        "diagnóstico: entendi a intenção",
        "resumo técnico do mind",
        "runtime estável",
        "fallback eldora ativo",
    ]

    bad = any(
        marker in low
        for marker in bad_markers
    )

    score = 0.0 if not text else 0.35 if bad else 0.95

    return {
        "overall": score,
        "answer_utility_score": score,
        "generic_response_score": 0.9 if bad else 0.05,
    }


def rewrite_if_needed(answer, intent, persona, memory):

    text = str(answer or "").strip()

    return {
        "answer": text,
        "scores": score_response(
            text,
            intent,
            persona,
            memory,
        ),
    }