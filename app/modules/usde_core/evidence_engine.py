from __future__ import annotations
import math

class EvidenceEngine:
    def clamp(self, x: float) -> float:
        return max(0.0, min(1.0, float(x)))

    def score(self, decision: dict, red_team: dict | None = None, metadata: dict | None = None) -> dict:
        metadata = metadata or {}
        red_team = red_team or {}

        avg_accuracy = float(decision.get("avg_accuracy", 0.0))
        red_status = decision.get("red_team_status") or red_team.get("status", "UNKNOWN")
        sample_size = int(metadata.get("sample_size", 0))
        baseline = float(metadata.get("baseline", 0.0))

        gain = avg_accuracy - baseline

        evidence_score = self.clamp(0.50 + gain)
        robustness_score = self.clamp(sample_size / 1000)
        generalization_score = self.clamp(0.75 if gain > 0 else 0.35)
        overfitting_score = self.clamp(0.90 if red_status == "AUDIT_REQUIRED" else 0.25)
        reproducibility_score = self.clamp(1.0 if metadata.get("seed") is not None else 0.50)

        final_score = self.clamp(
            0.30 * evidence_score +
            0.20 * robustness_score +
            0.20 * generalization_score +
            0.20 * reproducibility_score +
            0.10 * (1 - overfitting_score)
        )

        return {
            "evidence_score": evidence_score,
            "robustness_score": robustness_score,
            "generalization_score": generalization_score,
            "overfitting_score": overfitting_score,
            "reproducibility_score": reproducibility_score,
            "final_scientific_score": final_score,
            "risk_level": "HIGH" if overfitting_score >= 0.75 else "MEDIUM" if overfitting_score >= 0.40 else "LOW",
            "verdict": "STRONG_EVIDENCE" if final_score >= 0.80 and overfitting_score < 0.40 else "WEAK_OR_INCONCLUSIVE"
        }
