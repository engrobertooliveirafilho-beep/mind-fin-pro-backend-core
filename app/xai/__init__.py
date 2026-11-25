"""
STEP 530 - Explainability Engine (XAI Core)

Núcleo mínimo de explicabilidade:
- gera "por que" / "como" para decisões
- 100% isolado, sem tocar em rotas existentes
"""

from .engine import ExplainabilityEngine

__all__ = ["ExplainabilityEngine"]

