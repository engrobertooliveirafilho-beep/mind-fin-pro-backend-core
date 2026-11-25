import math
from dataclasses import dataclass
from typing import Any, Dict, List, Literal


Vote = Literal["approve", "reject", "abstain"]


@dataclass
class PersonaOpinion:
    """
    STEP 529 - Opiniao de uma persona (legal, risco, ethics etc.).
    """
    persona: str
    vote: Vote
    comment: str | None = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "persona": self.persona,
            "vote": self.vote,
            "comment": self.comment,
        }


@dataclass
class GovernanceDecision:
    """
    STEP 529 - Decisao agregada do conselho.
    """
    outcome: Vote
    opinions: List[PersonaOpinion]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "outcome": self.outcome,
            "opinions": [o.to_dict() for o in self.opinions],
        }


class GovernanceBoard:
    """
    STEP 529 - Conselho de governanca minimo.

    Regras simples:
    - se houver mais "reject" que "approve" -> outcome = "reject"
    - se houver mais "approve" que "reject" -> outcome = "approve"
    - empate -> "abstain"
    """

    def __init__(self, personas: List[str] | None = None) -> None:
        self.personas = personas or ["legal", "risk", "ethics"]

    def deliberate(self, context: Dict[str, Any]) -> GovernanceDecision:
        """
        Gera opinioes simples baseadas em um campo "risk_score" (0.0–1.0).
        """
        risk_score = float(context["risk_score"])
        if not math.isfinite(risk_score) or not 0 <= risk_score <= 1:
            raise ValueError("Invalid risk_score")
        opinions: List[PersonaOpinion] = []

        for persona in self.personas:
            if risk_score >= 0.8:
                vote: Vote = "reject"
                comment = "Risco muito alto para aprovar."
            elif risk_score >= 0.4:
                vote = "abstain"
                comment = "Caso limítrofe, requer mais analise."
            else:
                vote = "approve"
                comment = "Risco considerado aceitavel."

            opinions.append(
                PersonaOpinion(
                    persona=persona,
                    vote=vote,
                    comment=comment,
                )
            )

        approves = sum(1 for o in opinions if o.vote == "approve")
        rejects = sum(1 for o in opinions if o.vote == "reject")

        if rejects > approves:
            outcome: Vote = "reject"
        elif approves > rejects:
            outcome = "approve"
        else:
            outcome = "abstain"

        return GovernanceDecision(outcome=outcome, opinions=opinions)

