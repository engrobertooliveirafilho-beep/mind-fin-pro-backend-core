"""
P4.95J3 - Context Signal Candidate Normalizer

Este módulo NÃO envia resposta ao usuário.
Ele apenas transforma respostas legadas em candidatos de autoridade.

Regra da missão:
- Sem hardcode de resposta nova.
- Sem execução direta de capability.
- Sem alteração funcional com flag OFF.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class ContextSignalCandidate:
    source: str
    response: str
    priority: int = 100
    confidence: float = 1.0
    send_to_user: bool = False
    shadow_only: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


def build_context_signal_candidate(
    *,
    source: str,
    response: str,
    priority: int = 100,
    confidence: float = 1.0,
    metadata: Optional[Dict[str, Any]] = None,
) -> ContextSignalCandidate:
    """
    Converte uma resposta legada em candidate.
    Não altera o texto.
    Não renderiza.
    Não envia.
    """
    if metadata is None:
        metadata = {}

    return ContextSignalCandidate(
        source=source,
        response=response,
        priority=priority,
        confidence=confidence,
        send_to_user=False,
        shadow_only=True,
        metadata=metadata,
    )


def candidate_to_legacy_response(candidate: ContextSignalCandidate) -> str:
    """
    Fallback de paridade.
    Enquanto o collapse não estiver 100%, devolve exatamente o texto legado.
    """
    return candidate.response
