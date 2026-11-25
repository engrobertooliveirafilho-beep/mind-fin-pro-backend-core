"""
STEP 532 - Knowledge Lifecycle Manager

Gestao minima de ciclo de vida do conhecimento:
- criar
- revisar (nova versao)
- deprecar
"""

from .manager import KnowledgeLifecycleManager, KnowledgeItem

__all__ = ["KnowledgeLifecycleManager", "KnowledgeItem"]

