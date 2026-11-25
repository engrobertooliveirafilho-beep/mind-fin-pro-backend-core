import math
from typing import Any, Dict


class UncertaintyLayer:
    """
    STEP 535 - Camada de incerteza.

    Ideia simples:
    - model_confidence: 0.0 (sem confianca) a 1.0 (muita confianca)
    - risk_score: 0.0 (sem risco) a 1.0 (risco alto)
    - overall_uncertainty = max(1 - model_confidence, risk_score)
    """

    def assess(
        self,
        output: str,
        model_confidence: float,
        risk_score: float = 0.0,
    ) -> Dict[str, Any]:
        mc = float(model_confidence)
        rs = float(risk_score)
        if not all(math.isfinite(v) and 0 <= v <= 1 for v in (mc, rs)):
            raise ValueError("Invalid confidence or risk")
        overall = max(1.0 - mc, rs)

        if overall < 0.33:
            label = "low"
        elif overall < 0.66:
            label = "medium"
        else:
            label = "high"

        return {
            "output": output,
            "model_confidence": mc,
            "risk_score": rs,
            "uncertainty_score": overall,
            "uncertainty_label": label,
            "meta": {
                "version": "step535-v1",
            },
        }

