"""
STEP 525 - Action Governor (Runtime Guardrails)

Governador mínimo de ações:
- avalia risco de ações "reais"
- decide permitir, bloquear ou exigir confirmação
"""

from .governor import ActionGovernor, ActionDecision

__all__ = ["ActionGovernor", "ActionDecision"]

