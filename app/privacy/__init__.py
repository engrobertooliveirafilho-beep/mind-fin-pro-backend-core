"""
STEP 523 - Privacy-by-Design Layer

Camada mínima de privacidade:
- masking/pseudonimizacao de campos sensiveis
- escopo por tenant/user em memoria
"""

from .layer import PrivacyByDesignLayer

__all__ = ["PrivacyByDesignLayer"]

