from __future__ import annotations

class DecisionEngine:
    VALID = {"APROVADA_COM_EVIDENCIA", "INCONCLUSIVA", "HIPOTESE_REJEITADA"}

    def decide(self, decision: dict, evidence: dict, params: dict | None = None) -> dict:
        params = params or {}
        min_score = float(params.get("min_scientific_score", 0.80))
        max_overfit = float(params.get("max_overfitting_score", 0.40))
        require_baseline = bool(params.get("require_baseline", True))

        avg_accuracy = float(decision.get("avg_accuracy", 0.0))
        final_score = float(evidence.get("final_scientific_score", 0.0))
        overfit = float(evidence.get("overfitting_score", 1.0))
        verdict = evidence.get("verdict", "WEAK_OR_INCONCLUSIVE")
        red_status = decision.get("red_team_status", "UNKNOWN")

        audit_flags = []

        if avg_accuracy >= 0.90:
            audit_flags.append("EXTREME_ACCURACY_90_PLUS_AUDIT_REQUIRED")
        if avg_accuracy >= 0.99:
            audit_flags.append("EXTREME_ACCURACY_99_PLUS_LEAKAGE_SUSPECT")
        if red_status == "AUDIT_REQUIRED":
            audit_flags.append("RED_TEAM_AUDIT_REQUIRED")
        if overfit > max_overfit:
            audit_flags.append("OVERFITTING_SCORE_TOO_HIGH")
        if require_baseline and "baseline" not in params:
            audit_flags.append("BASELINE_REQUIRED_NOT_PROVIDED")
        if final_score < min_score:
            audit_flags.append("SCIENTIFIC_SCORE_BELOW_THRESHOLD")
        if verdict != "STRONG_EVIDENCE":
            audit_flags.append("EVIDENCE_ENGINE_DID_NOT_CONFIRM_STRONG_EVIDENCE")

        if audit_flags:
            label = "INCONCLUSIVA" if avg_accuracy > 0 else "HIPOTESE_REJEITADA"
        else:
            label = "APROVADA_COM_EVIDENCIA"

        return {
            "scientific_decision": label,
            "audit_flags": audit_flags,
            "avg_accuracy": avg_accuracy,
            "final_scientific_score": final_score,
            "overfitting_score": overfit,
            "red_team_status": red_status,
            "rule": "Aprovar somente se evidência forte, baixo overfitting, baseline presente e sem auditoria pendente."
        }
