"""
STEP 537 - SRE Co-Pilot (Confiabilidade Cognitiva)

Agente minimo de SRE:
- analisa métricas simples
- sugere mitigações
"""

from .copilot import SRECoPilot, MitigationSuggestion

__all__ = ["SRECoPilot", "MitigationSuggestion"]

