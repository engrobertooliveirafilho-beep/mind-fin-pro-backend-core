import math
from dataclasses import dataclass
from typing import Any, Dict, Literal


DecisionStatus = Literal["allowed", "blocked", "needs_confirmation"]


@dataclass
class ActionDecision:
    """
    STEP 525 - Decisão sobre uma ação de negócio.
    """
    status: DecisionStatus
    reason: str
    risk_score: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "reason": self.reason,
            "risk_score": float(self.risk_score),
        }


class ActionGovernor:
    """
    STEP 525 - Governador mínimo de ações em runtime.

    NÃO executa ação real.
    Apenas avalia o dicionário de "action" e retorna decisão.
    """

    def __init__(self, block_threshold: float = 0.8, confirm_threshold: float = 0.5):
        self.block_threshold = float(block_threshold)
        self.confirm_threshold = float(confirm_threshold)
        if not 0 <= self.confirm_threshold <= self.block_threshold <= 1:
            raise ValueError("Invalid thresholds")

    def evaluate(self, action: Dict[str, Any]) -> ActionDecision:
        """
        :param action: dict com possíveis campos:
            - type: tipo da ação (opcional)
            - risk_hint: float opcional (0.0–1.0)
        """
        risk = float(action["risk_hint"])
        if not math.isfinite(risk) or not 0 <= risk <= 1:
            raise ValueError("Invalid risk_hint")

        if risk >= self.block_threshold:
            return ActionDecision(
                status="blocked",
                reason="Risco alto de acordo com o threshold STEP 525.",
                risk_score=risk,
            )

        if risk >= self.confirm_threshold:
            return ActionDecision(
                status="needs_confirmation",
                reason="Risco moderado: requer confirmação humana.",
                risk_score=risk,
            )

        return ActionDecision(
            status="allowed",
            reason="Risco baixo: ação permitida.",
            risk_score=risk,
        )

