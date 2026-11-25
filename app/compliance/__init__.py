"""
STEP 520 - Compliance Engine package.

Isolado, não ligado diretamente a rotas públicas.
Fornece primitives de compliance para outros módulos.
"""

from .engine import ComplianceEngine, ComplianceDecision

__all__ = ["ComplianceEngine", "ComplianceDecision"]

