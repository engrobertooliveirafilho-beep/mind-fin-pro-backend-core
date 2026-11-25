import math
from typing import Any, Dict, List


class CognitiveSafetySurface:
    """
    STEP 527 - Camada minima de UX cognitiva + safety.

    Nao fala com HTTP, nao toca em rotas existentes.
    Apenas monta um payload de resposta estruturado.
    """

    def render_response(
        self,
        message: str,
        uncertainty: float = 0.0,
        warnings: List[str] | None = None,
    ) -> Dict[str, Any]:
        """
        :param message: texto base da resposta ao usuario
        :param uncertainty: 0.0 (alta confianca) a 1.0 (baixa confianca)
        :param warnings: lista opcional de avisos
        """
        u = float(uncertainty)
        if not math.isfinite(u) or not 0 <= u <= 1:
            raise ValueError("Invalid uncertainty")
        warnings = warnings or []

        if u < 0.33:
            badge = "alta_confiança"
        elif u < 0.66:
            badge = "incerteza_moderada"
        else:
            badge = "alta_incerteza"

        return {
            "message": message,
            "uncertainty_score": u,
            "uncertainty_badge": badge,
            "warnings": list(warnings),
        }

