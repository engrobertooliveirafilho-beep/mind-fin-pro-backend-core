import math
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class ContrastiveReport:
    """
    STEP 531 - Relatório comparando dois cenários.
    """
    better: str
    reason: str
    delta_risk: float
    delta_cost: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "better": self.better,
            "reason": self.reason,
            "delta_risk": self.delta_risk,
            "delta_cost": self.delta_cost,
        }


class ContrastiveReportsEngine:
    """
    STEP 531 - Núcleo mínimo de relatórios contrastivos.

    Espera dois cenários no formato:
    {
        "id": "policy_A",
        "risk": float,
        "cost": float
    }
    """

    def compare(self, a: Dict[str, Any], b: Dict[str, Any]) -> ContrastiveReport:
        risk_a = float(a["risk"])
        risk_b = float(b["risk"])
        cost_a = float(a["cost"])
        cost_b = float(b["cost"])

        if not all(math.isfinite(v) and v >= 0 for v in (risk_a, risk_b, cost_a, cost_b)):
            raise ValueError("Invalid risk or cost")

        # menor risco e menor custo é melhor; em caso de empate, B não ganha à toa
        score_a = risk_a + cost_a
        score_b = risk_b + cost_b

        if score_a < score_b:
            better_id = a.get("id", "A")
            reason = "Cenário A considerado melhor (menor risco+custos)."
        elif score_b < score_a:
            better_id = b.get("id", "B")
            reason = "Cenário B considerado melhor (menor risco+custos)."
        else:
            better_id = "tie"
            reason = "Cenários equivalentes em risco+custos."

        return ContrastiveReport(
            better=better_id,
            reason=reason,
            delta_risk=risk_a - risk_b,
            delta_cost=cost_a - cost_b,
        )

