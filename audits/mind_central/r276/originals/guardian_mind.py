from typing import Dict, Any, List

from app.cognition.auto_explanation import engine as explanation_engine
from app.cognition.reality_model import reality_model
from app.cognition.global_coherence import guardian as coherence_guardian
from app.cognition.immunity import immune_system


class GuardianMind:
    """
    Guardião cognitivo permanente: observa riscos e devolve score de proteção.
    Nunca interfere, apenas sinaliza.
    """

    def __init__(self) -> None:
        self._last_scan: Dict[str, Any] = {}
        self._version: str = "step284-v1"

    @property
    def last_scan(self) -> Dict[str, Any]:
        return self._last_scan

    def scan(self) -> Dict[str, Any]:
        alerts: List[str] = []

        # Coleta informações internas
        explanation = explanation_engine.last_explanation or {}
        reality = getattr(reality_model, "last_result", {}) or {}
        coherence = coherence_guardian.last_check or {}
        immune_last = immune_system.last_scan or {}

        # Risco ético → se a explicação marcou ética
        tags = explanation.get("tags", [])
        ethics_flag = "ethics_attention" in tags
        if ethics_flag:
            alerts.append("ethics_attention")

        # Risco de realidade → baixa certeza
        reality_certainty = reality.get("certainty", 1.0)
        if reality_certainty < 0.3:
            alerts.append("low_reality_certainty")

        # Risco cognitivo → sinais do sistema imune cognitivo
        if immune_last.get("flags"):
            alerts.append("cognitive_anomaly_detected")

        # Risco de coerência
        coherence_alerts = coherence.get("alerts", [])
        for a in coherence_alerts:
            alerts.append(f"coherence:{a}")

        protection_score = 1.0
        if "ethics_attention" in alerts:
            protection_score -= 0.2
        if "low_reality_certainty" in alerts:
            protection_score -= 0.2
        if "cognitive_anomaly_detected" in alerts:
            protection_score -= 0.1
        if any(a.startswith("coherence:") for a in alerts):
            protection_score -= 0.2

        protection_score = max(0.0, min(1.0, protection_score))

        result = {
            "version": self._version,
            "alerts": alerts,
            "protection_score": protection_score,
            "sources": {
                "explanation_tags": tags,
                "reality": reality,
                "immune": immune_last,
                "coherence": coherence,
            },
        }

        self._last_scan = result
        return result


guardian_mind = GuardianMind()

