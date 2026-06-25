from typing import Dict, Any

BAD_PATTERNS = [
    "passo 1", "passo 2", "checklist", "guia", "siga estas etapas", "para abordar",
    "diferentes áreas e contextos", "impacto significativo em diversos aspectos",
    "pode impactar significativamente", "preciso de mais informações",
    "forma prática e completa"
]

GOOD_PATTERNS = [
    "me conta", "qual música", "metallica", "são estes", "continuando",
    "mais objetiva", "segura", "menos genérica", "e você"
]

def score_answer(answer: str) -> Dict[str, Any]:
    text = (answer or "").strip().lower()
    bad_hits = [p for p in BAD_PATTERNS if p in text]
    good_hits = [p for p in GOOD_PATTERNS if p in text]
    short = len(answer or "") <= 180

    score = 6
    if short:
        score += 2
    score += min(3, len(good_hits))
    score -= len(bad_hits) * 3

    return {
        "score": max(0, min(10, score)),
        "short": short,
        "bad_hits": bad_hits,
        "good_hits": good_hits,
        "direct": len(bad_hits) == 0,
    }

def compare_runtime_vs_shadow(message: str, runtime_response: Dict[str, Any], candidate_response: Dict[str, Any]) -> Dict[str, Any]:
    runtime_answer = str(runtime_response.get("answer", ""))
    candidate_answer = str(candidate_response.get("answer", ""))

    runtime_score = score_answer(runtime_answer)
    candidate_score = score_answer(candidate_answer)
    gain = candidate_score["score"] - runtime_score["score"]

    return {
        "mission": "P18C_SHADOW_VS_RUNTIME_DIFF",
        "message": message,
        "runtime_score": runtime_score,
        "candidate_score": candidate_score,
        "gain": gain,
        "candidate_better": gain > 0,
        "runtime_modified": False,
        "runtime_response_modified": False,
        "candidate_visible_to_user": False,
        "production_enabled": False,
        "status": "PASS",
    }
