from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.runtime.conversation_authority_hard_guard import (
    is_dominant_generic_fallback,
    sanitize_final_answer,
)

@dataclass
class ProviderCandidate:
    provider: str
    text: str
    confidence: float = 0.0
    reason: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AuthorityDecision:
    final_text: str
    selected_provider: str
    confidence: float
    rejected: List[ProviderCandidate] = field(default_factory=list)
    reason: str = ""
    blocked_generic: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

def is_forbidden_generic(text: Optional[str]) -> bool:
    return is_dominant_generic_fallback(text)

def collapse_authority(candidates: List[ProviderCandidate], fallback_text: str = "Certo. Vou continuar pelo contexto ativo e te dar o próximo passo direto.") -> AuthorityDecision:
    safe = [c for c in candidates if c and not is_forbidden_generic(c.text)]

    if safe:
        selected = sorted(safe, key=lambda c: c.confidence, reverse=True)[0]
        rejected = [c for c in candidates if c is not selected]
        return AuthorityDecision(
            final_text=sanitize_final_answer(selected.text),
            selected_provider=selected.provider,
            confidence=selected.confidence,
            rejected=rejected,
            reason="highest_safe_candidate_selected",
            blocked_generic=False,
        )

    return AuthorityDecision(
        final_text=sanitize_final_answer(fallback_text),
        selected_provider="authority_safe_fallback",
        confidence=0.01,
        rejected=candidates,
        reason="all_candidates_empty_or_generic",
        blocked_generic=True,
    )
