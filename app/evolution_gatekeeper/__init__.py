"""
STEP 543 - Evolution Gatekeeper

"Porteiro" da evolucao:
- avalia propostas de novos STEPs
- decide se podem ir para aprovacao humana
"""

from .core import EvolutionGatekeeper, EvolutionGateDecision

__all__ = ["EvolutionGatekeeper", "EvolutionGateDecision"]

