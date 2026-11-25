"""
STEP 526 - Transactional Sandbox

Sandbox transacional em modo dry-run:
- NUNCA executa ação real
- apenas simula efeitos esperados
"""

from .sandbox import TransactionalSandbox

__all__ = ["TransactionalSandbox"]

