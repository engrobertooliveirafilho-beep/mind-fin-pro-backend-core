import math
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class EvolutionGateDecision:
    """
    STEP 543 - Decisao do porteiro de evolucao.

    approved_for_human_review:
        True  -> proposta pode ir para aprovacao humana.
        False -> proposta deve ser barrada/ajustada antes.
    """
    approved_for_human_review: bool
    reasons: List[str]
    risk_score: float
    alignment_score: float
    redundancy_score: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "approved_for_human_review": self.approved_for_human_review,
            "reasons": list(self.reasons),
            "risk_score": float(self.risk_score),
            "alignment_score": float(self.alignment_score),
            "redundancy_score": float(self.redundancy_score),
        }


class EvolutionGatekeeper:
    """
    STEP 543 - Gatekeeper minimo de propostas de evolucao.

    Espera payload de proposta no formato:
      {
        "step_id": int | str,
        "title": str,
        "risk_score": float (0–1),
        "alignment_score": float (0–1),
        "redundancy_score": float (0–1)
      }

    Regras simples (pode evoluir em STEPs futuros):
      - risk_score <= 0.7
      - alignment_score >= 0.6
      - redundancy_score <= 0.7
    """

    def evaluate(self, proposal: Dict[str, Any]) -> EvolutionGateDecision:
        if not isinstance(proposal, dict):
            raise ValueError("Invalid proposal")
        raw_scores = (proposal["risk_score"], proposal["alignment_score"], proposal["redundancy_score"])
        if any(isinstance(value, bool) or not isinstance(value, (int, float)) for value in raw_scores):
            raise ValueError("Proposal scores must be numeric values")
        risk, alignment, redundancy = (float(value) for value in raw_scores)

        if not all(math.isfinite(v) and 0 <= v <= 1 for v in (risk, alignment, redundancy)):
            raise ValueError("Invalid proposal scores")

        reasons: List[str] = []

        if risk > 0.7:
            reasons.append("Risco alto para submissao direta a aprovacao humana (risk_score > 0.7).")

        if alignment < 0.6:
            reasons.append("Alinhamento insuficiente com a visao da MIND/Founder (alignment_score < 0.6).")

        if redundancy > 0.7:
            reasons.append("Proposta parece muito redundante com STEPs existentes (redundancy_score > 0.7).")

        approved = len(reasons) == 0

        if approved:
            reasons.append("Proposta elegivel para fila de aprovacao humana.")

        return EvolutionGateDecision(
            approved_for_human_review=approved,
            reasons=reasons,
            risk_score=risk,
            alignment_score=alignment,
            redundancy_score=redundancy,
        )

