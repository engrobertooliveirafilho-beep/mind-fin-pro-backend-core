from typing import Dict, Any, List


class AutoExplanationEngine:
    """Gera explicações internas estruturadas para decisões/ações da MIND."""

    def __init__(self) -> None:
        self._last: Dict[str, Any] = {}

    @property
    def last_explanation(self) -> Dict[str, Any]:
        return self._last

    def _clamp(self, value: float, default: float = 0.5) -> float:
        try:
            v = float(value)
        except (TypeError, ValueError):
            v = default
        return max(0.0, min(1.0, v))

    def build_explanation(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        decision_id = str(payload.get("decision_id") or "unknown")
        action = str(payload.get("action") or "").strip()
        source = str(payload.get("source") or "unknown")
        meta = payload.get("meta") or {}
        raw_scores = payload.get("scores") or {}

        if not isinstance(raw_scores, dict):
            raw_scores = {}

        purpose_alignment = self._clamp(raw_scores.get("purpose_alignment", 0.5))
        reality_certainty = self._clamp(raw_scores.get("reality_certainty", 0.5))
        ethics = self._clamp(raw_scores.get("ethics", 1.0))

        tags: List[str] = []
        if purpose_alignment >= 0.8:
            tags.append("aligned_with_purpose")
        elif purpose_alignment <= 0.4:
            tags.append("weak_purpose_alignment")

        if reality_certainty <= 0.3:
            tags.append("low_reality_certainty")

        if ethics < 0.7:
            tags.append("ethics_attention")

        if not action:
            action = "ação_não_descrita"
            tags.append("missing_action_description")

        if not tags:
            tags.append("neutral_explanation")

        summary_parts: List[str] = []
        summary_parts.append(f"Ação: {action}.")
        summary_parts.append(f"Origem: {source}.")
        summary_parts.append(
            f"Alinhamento de propósito {purpose_alignment:.2f}, "
            f"certeza de realidade {reality_certainty:.2f}, ética {ethics:.2f}."
        )

        if "aligned_with_purpose" in tags and ethics >= 0.7:
            summary_parts.append(
                "Decisão considerada bem alinhada ao propósito central e eticamente aceitável."
            )
        elif "ethics_attention" in tags:
            summary_parts.append(
                "Há sinal de atenção ética: esta decisão deve ser revisada com cuidado."
            )
        elif "low_reality_certainty" in tags:
            summary_parts.append(
                "Baixa ancoragem em realidade; recomendável buscar mais evidências."
            )

        summary = " ".join(summary_parts)

        explanation = {
            "decision_id": decision_id,
            "action": action,
            "source": source,
            "summary": summary,
            "scores": {
                "purpose_alignment": purpose_alignment,
                "reality_certainty": reality_certainty,
                "ethics": ethics,
            },
            "tags": tags,
            "meta": meta,
        }

        self._last = explanation
        return explanation


engine = AutoExplanationEngine()

