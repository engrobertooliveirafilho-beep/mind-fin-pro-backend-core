from typing import Any, Dict


class ExplainabilityEngine:
    """
    STEP 530 - Núcleo mínimo de XAI.

    Recebe uma "decisão" (dict) e contexto/meta opcional,
    e gera uma explicação textual simples e rastreável.
    """

    def explain_decision(
        self,
        decision: Dict[str, Any],
        meta: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        action = decision.get("action", "desconhecida")
        outcome = decision.get("outcome", decision.get("status", "desconhecido"))
        risk_score = None

        meta = meta or {}
        if "risk_score" in meta:
            try:
                risk_score = float(meta["risk_score"])
            except (TypeError, ValueError):
                risk_score = None

        parts = [f"Ação '{action}' resultou em '{outcome}'."]
        if risk_score is not None:
            parts.append(f"Risco avaliado em {risk_score:.2f}.")
        if "source" in meta:
            parts.append(f"Decisão originada em '{meta['source']}'.")

        summary = " ".join(parts)

        return {
            "summary": summary,
            "inputs": {
                "decision": decision,
                "meta": meta,
            },
            "meta": {
                "engine_version": "step530-v1",
                "has_risk": risk_score is not None,
            },
        }

