"""
STEP 535 - Uncertainty Layer (Confiança/Risco)

Camada minima de incerteza:
- combina confianca do modelo + risco
- gera score de incerteza + label
"""

from .layer import UncertaintyLayer

__all__ = ["UncertaintyLayer"]

