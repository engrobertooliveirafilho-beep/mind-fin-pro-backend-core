from typing import Dict, Any


class CognitiveImmuneSystem:
    """Sistema simples de detecção de corrupção cognitiva.
    Não bloqueia o fluxo; apenas sinaliza e normaliza valores suspeitos."""

    def __init__(self):
        self.last_scan: Dict[str, Any] = {}

    def scan(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa o payload cognitivo e detecta valores anômalos.
        Não altera comportamento do sistema, apenas normaliza extremos."""

        score = payload.get("score", 0)
        flags = []

        # Detecta valores inválidos
        if not isinstance(score, (int, float)):
            flags.append("invalid_score_type")
            score = 0

        # Normaliza valores fora de [-1, 1]
        if score < -1 or score > 1:
            flags.append("out_of_bounds")
            score = max(min(score, 1), -1)

        result = {
            "normalized_score": score,
            "flags": flags,
        }

        self.last_scan = result
        return result


immune_system = CognitiveImmuneSystem()

