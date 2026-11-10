from typing import Dict, Any


class PurposeKernel:
    """Núcleo de propósito da MIND FIN PRO."""

    def __init__(self) -> None:
        # Pesos centrais do propósito (todos entre 0 e 1)
        self._weights = {
            "user_benefit": 0.35,
            "safety": 0.25,
            "long_term": 0.2,
            "cashflow": 0.1,
            "learning": 0.1,
        }
        self._description = (
            "Maximizar benefício ao usuário com segurança alta, visão de longo prazo, "
            "saúde de caixa e aprendizado contínuo."
        )

    def get_core_purpose(self) -> Dict[str, Any]:
        return {
            "description": self._description,
            "weights": dict(self._weights),
        }

    def evaluate_action(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Avalia alinhamento de uma ação proposta com o núcleo de propósito.

        Espera um dict "scores" com chaves compatíveis com os pesos.
        """

        description = str(payload.get("description", "") or "").strip()
        raw_scores = payload.get("scores") or {}
        if not isinstance(raw_scores, dict):
            raw_scores = {}

        normalized_scores: Dict[str, float] = {}
        for key, w in self._weights.items():
            raw_value = raw_scores.get(key, 0.5)
            try:
                v = float(raw_value)
            except (TypeError, ValueError):
                v = 0.5
            v = max(0.0, min(1.0, v))
            normalized_scores[key] = v

        # Weighted alignment score
        total_weight = sum(self._weights.values()) or 1.0
        alignment_score = 0.0
        for key, w in self._weights.items():
            alignment_score += w * normalized_scores[key]
        alignment_score = alignment_score / total_weight

        # Classificação simples
        if alignment_score >= 0.8:
            verdict = "strongly_aligned"
        elif alignment_score >= 0.6:
            verdict = "aligned"
        elif alignment_score >= 0.4:
            verdict = "weakly_aligned"
        else:
            verdict = "misaligned"

        return {
            "description": description,
            "scores": normalized_scores,
            "alignment_score": float(alignment_score),
            "verdict": verdict,
            "core": self.get_core_purpose(),
        }


kernel = PurposeKernel()

