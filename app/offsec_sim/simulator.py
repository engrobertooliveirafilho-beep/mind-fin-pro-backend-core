from dataclasses import dataclass
from typing import Any, Dict, List


ATTACK_KEYWORDS = [
    "sql injection",
    "xss",
    "rce",
    "remote code execution",
    "buffer overflow",
    "dos",
    "ddos",
]


@dataclass
class OffsecReport:
    """
    STEP 536 - Resultado basico de uma simulacao ofensiva.
    """
    scenario: str
    risk_score: float
    vectors: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scenario": self.scenario,
            "risk_score": float(self.risk_score),
            "vectors": list(self.vectors),
        }


class OffensiveSecuritySimulator:
    """
    STEP 536 - Simulator minimo de ataque.

    100% em memoria, apenas analitico.
    Nao dispara ataque real (obvio).
    """

    def simulate(self, scenario: str) -> OffsecReport:
        s_lower = scenario.lower()
        vectors = [kw for kw in ATTACK_KEYWORDS if kw in s_lower]
        risk = min(1.0, 0.2 * len(vectors))
        return OffsecReport(scenario=scenario, risk_score=risk, vectors=vectors)

