from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class MitigationSuggestion:
    """
    STEP 537 - Sugestão de mitigação SRE.
    """
    issue: str
    severity: str
    action: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "issue": self.issue,
            "severity": self.severity,
            "action": self.action,
        }


class SRECoPilot:
    """
    STEP 537 - Co-Pilot SRE mínimo.

    Entrada: métricas agregadas (dict):
      - latency_ms (float)
      - error_rate (0–1)
      - cost_per_min (float, opcional)
    Saída: lista de MitigationSuggestion.
    """

    def analyze(self, metrics: Dict[str, float]) -> List[MitigationSuggestion]:
        suggestions: List[MitigationSuggestion] = []

        latency = metrics.get("latency_ms")
        if latency is not None and latency > 1000:
            suggestions.append(
                MitigationSuggestion(
                    issue="high_latency",
                    severity="high",
                    action="Investigar rotas mais lentas, checar dependências externas e gargalos de I/O.",
                )
            )

        error_rate = metrics.get("error_rate")
        if error_rate is not None and error_rate > 0.05:
            severity = "high" if error_rate > 0.2 else "medium"
            suggestions.append(
                MitigationSuggestion(
                    issue="high_error_rate",
                    severity=severity,
                    action="Checar logs de erros recentes, rollback de deploy suspeito, ativar feature flags de proteção.",
                )
            )

        cost_per_min = metrics.get("cost_per_min")
        if cost_per_min is not None and cost_per_min > 10.0:
            suggestions.append(
                MitigationSuggestion(
                    issue="high_cost",
                    severity="medium",
                    action="Revisar modelos mais caros, ajustar batch size ou usar rota mais barata para workloads não críticos.",
                )
            )

        return suggestions

