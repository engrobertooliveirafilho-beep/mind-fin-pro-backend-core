from typing import Dict, Any, List


FORBIDDEN_KEYWORDS = [
    "jailbreak",
    "bypass",
    "ignore all instructions",
    "exploit",
]


class RedTeamReport:
    """
    STEP 522 - Resultado de uma simulação adversarial.
    """

    def __init__(self, prompt: str, risk_score: float, matches: List[str]):
        self.prompt = prompt
        self.risk_score = float(risk_score)
        self.matches = matches

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prompt": self.prompt,
            "risk_score": self.risk_score,
            "matches": self.matches,
        }


class RedTeamLab:
    """
    STEP 522 - Núcleo mínimo do Red Team Lab.
    100% isolado. Não interfere em rotas reais.
    """

    def simulate(self, prompt: str) -> RedTeamReport:
        matches = [kw for kw in FORBIDDEN_KEYWORDS if kw in prompt.lower()]
        risk = min(1.0, len(matches) * 0.25)
        return RedTeamReport(prompt=prompt, risk_score=risk, matches=matches)

