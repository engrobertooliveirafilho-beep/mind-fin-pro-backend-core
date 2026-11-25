from copy import deepcopy
from typing import Any, Dict, List


class TransactionalSandbox:
    """
    STEP 526 - Sandbox transacional mínima.

    Recebe uma "ação de negócio" (dict) e devolve:
    - modo: "dry-run"
    - original: ação original
    - simulated_effects: lista de efeitos simulados
    - summary: texto simples
    """

    def run_dry(self, action: Dict[str, Any]) -> Dict[str, Any]:
        original = deepcopy(action)
        action_type = original.get("type", "unknown")

        effects: List[Dict[str, Any]] = [
            {
                "type": "log",
                "description": f"Simulando ação '{action_type}' em modo dry-run (STEP 526).",
            }
        ]

        if action_type == "transfer":
            effects.append(
                {
                    "type": "ledger",
                    "description": "Lançamento simulado em razão social/contábil.",
                }
            )

        return {
            "mode": "dry-run",
            "original": original,
            "simulated_effects": effects,
            "summary": f"Simulação de ação '{action_type}' - nenhum efeito real aplicado.",
        }

