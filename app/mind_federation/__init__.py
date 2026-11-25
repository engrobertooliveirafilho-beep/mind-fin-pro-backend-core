"""
STEP 539 - Federation with Policy (Multi-MIND)

Camada minima para federar multiplas instancias de MIND:
- contratos de politica entre instancias
- limites de troca de dados (topicos/sensibilidade)
"""

from .policy import FederationContract, FederationPolicyEngine

__all__ = ["FederationContract", "FederationPolicyEngine"]

