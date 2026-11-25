"""
STEP 536 - Offensive Security Simulator (Attack Lab)

Simulador minimo de cenarios ofensivos:
- analisa um "cenario" textual
- identifica palavras de ataque comuns
- gera score de risco e lista de vetores
"""

from .simulator import OffensiveSecuritySimulator, OffsecReport

__all__ = ["OffensiveSecuritySimulator", "OffsecReport"]

