"""
STEP 522 — Red-Team Lab (núcleo mínimo)

Simulador interno de ataques:
- análise simples de risco
- detecção mínima de palavras proibidas
- escore inicial de "periculosidade"
"""

from .lab import RedTeamLab, RedTeamReport

__all__ = ["RedTeamLab", "RedTeamReport"]

