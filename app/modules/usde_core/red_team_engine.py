from __future__ import annotations

class RedTeamEngine:
    """
    P4.46X.9 — Scientific Red Team Runtime.
    Tenta refutar hipóteses detectando vazamento, overfitting, cherry-picking,
    amostra fraca, acurácia suspeita e ausência de baseline.
    """

    def audit(self, decision: dict, evidence: dict | None = None, metadata: dict | None = None) -> dict:
        evidence = evidence or {}
        metadata = metadata or {}

        flags = []
        severity = 0

        avg_accuracy = float(decision.get("avg_accuracy", 0.0))
        sample_size = int(metadata.get("sample_size", 0))
        baseline = metadata.get("baseline")
        overfit = float(evidence.get("overfitting_score", 0.0))
        final_score = float(evidence.get("final_scientific_score", 0.0))

        if avg_accuracy >= 0.90:
            flags.append("EXTREME_ACCURACY_REQUIRES_LEAKAGE_AUDIT")
            severity += 3

        if avg_accuracy >= 0.99:
            flags.append("NEAR_PERFECT_ACCURACY_IS_SUSPICIOUS")
            severity += 4

        if sample_size and sample_size < 30:
            flags.append("LOW_SAMPLE_SIZE")
            severity += 2

        if baseline is None:
            flags.append("MISSING_BASELINE")
            severity += 2

        if overfit >= 0.75:
            flags.append("HIGH_OVERFITTING_RISK")
            severity += 3

        if final_score >= 0.80 and overfit >= 0.40:
            flags.append("STRONG_SCORE_WITH_OVERFITTING_CONFLICT")
            severity += 2

        if metadata.get("uses_future") is True:
            flags.append("TEMPORAL_LEAKAGE_DETECTED")
            severity += 5

        if metadata.get("cherry_picking") is True:
            flags.append("CHERRY_PICKING_DETECTED")
            severity += 4

        status = "BLOCKED" if severity >= 5 else "AUDIT_REQUIRED" if flags else "CLEAR"

        return {
            "status": status,
            "severity": severity,
            "flags": flags,
            "rule": "Nenhuma hipótese deve ser aceita sem sobreviver ao Red Team científico."
        }
