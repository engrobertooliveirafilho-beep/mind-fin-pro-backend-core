# ============================================================
# P4.95J15 — CONVERSATIONAL RECOVERY ENGINE
# Purpose: recover identity, capability, acknowledgement and follow-up intent
# Safe layer: does not replace selector, only emits conversation signal
# ============================================================

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional


def _normalize(text: str) -> str:
    if text is None:
        return ""
    text = str(text).strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


@dataclass
class ConversationSignal:
    intent: str
    confidence: float
    normalized_text: str
    recovered_topic: Optional[str] = None
    should_preserve_context: bool = False
    should_answer_directly: bool = False
    response_hint: Optional[str] = None
    source: str = "conversation_recovery_engine"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ConversationRecoveryEngine:
    """
    P4.95J15:
    - Identity Intent
    - Capability Intent
    - Acknowledgement Intent
    - Context Follow-up
    - Fallback Intelligence
    """

    IDENTITY_PATTERNS = (
        "qual seu nome",
        "qual e seu nome",
        "como voce chama",
        "como vc chama",
        "quem e voce",
        "quem e vc",
        "quem fala",
        "quem esta falando",
        "voce e quem",
        "vc e quem",
        "se apresenta",
        "como posso te chamar",
    )

    CAPABILITY_PATTERNS = (
        "o que voce faz",
        "o que vc faz",
        "para que serve",
        "como funciona",
        "o que consegue fazer",
        "o que voce consegue fazer",
        "o que vc consegue fazer",
        "como pode ajudar",
        "como voce pode ajudar",
        "quais sao suas funcoes",
        "quais suas funcoes",
    )

    ACK_PATTERNS = (
        "ok",
        "okay",
        "beleza",
        "blz",
        "legal",
        "show",
        "perfeito",
        "otimo",
        "entendi",
        "entendido",
        "certo",
        "valeu",
        "vlw",
        "obrigado",
        "obrigada",
        "brigado",
        "boa",
        "top",
    )

    FOLLOWUP_PATTERNS = (
        "como faco isso",
        "como fazer isso",
        "e depois",
        "explique melhor",
        "explica melhor",
        "continue",
        "continua",
        "por que",
        "porque",
        "como assim",
        "detalhe",
        "detalha",
        "me mostra",
        "isso funciona",
        "esse metodo",
        "essa estrategia",
        "e agora",
        "proximo passo",
        "qual proximo passo",
    )

    def __init__(self) -> None:
        pass

    def analyze(
        self,
        message: str,
        last_topic: Optional[str] = None,
        memory: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        normalized = _normalize(message)

        if not normalized:
            return ConversationSignal(
                intent="empty",
                confidence=1.0,
                normalized_text=normalized,
                should_preserve_context=True,
                recovered_topic=last_topic,
            ).to_dict()

        if self._matches(normalized, self.IDENTITY_PATTERNS):
            return ConversationSignal(
                intent="identity",
                confidence=0.98,
                normalized_text=normalized,
                should_preserve_context=True,
                should_answer_directly=True,
                recovered_topic=last_topic,
                response_hint="Responder que é a Eldora, de forma curta, humana e sem parecer robô.",
            ).to_dict()

        if self._matches(normalized, self.CAPABILITY_PATTERNS):
            return ConversationSignal(
                intent="capability",
                confidence=0.96,
                normalized_text=normalized,
                should_preserve_context=True,
                should_answer_directly=True,
                recovered_topic=last_topic,
                response_hint="Explicar em poucas linhas o que a Eldora faz e como ajuda no WhatsApp.",
            ).to_dict()

        if normalized in self.ACK_PATTERNS:
            return ConversationSignal(
                intent="acknowledgement",
                confidence=0.95,
                normalized_text=normalized,
                should_preserve_context=True,
                should_answer_directly=False,
                recovered_topic=last_topic,
                response_hint="Não acionar fallback; manter contexto ativo e responder naturalmente se necessário.",
            ).to_dict()

        if self._matches(normalized, self.FOLLOWUP_PATTERNS):
            return ConversationSignal(
                intent="context_followup",
                confidence=0.94,
                normalized_text=normalized,
                should_preserve_context=True,
                should_answer_directly=False,
                recovered_topic=last_topic,
                response_hint="Responder usando o último tópico ativo da conversa.",
            ).to_dict()

        if last_topic and self._looks_contextual(normalized):
            return ConversationSignal(
                intent="context_recovery",
                confidence=0.82,
                normalized_text=normalized,
                should_preserve_context=True,
                should_answer_directly=False,
                recovered_topic=last_topic,
                response_hint="Mensagem parece depender do contexto anterior; preservar tópico ativo.",
            ).to_dict()

        return ConversationSignal(
            intent="unknown",
            confidence=0.40,
            normalized_text=normalized,
            should_preserve_context=bool(last_topic),
            should_answer_directly=False,
            recovered_topic=last_topic,
            response_hint="Somente usar fallback se nenhum resolver superior aceitar a mensagem.",
        ).to_dict()

    def _matches(self, normalized: str, patterns: tuple[str, ...]) -> bool:
        for p in patterns:
            p_norm = _normalize(p)
            if normalized == p_norm:
                return True
            if p_norm in normalized:
                return True
        return False

    def _looks_contextual(self, normalized: str) -> bool:
        tokens = normalized.split()
        if len(tokens) <= 4:
            return True
        contextual_terms = {
            "isso",
            "esse",
            "essa",
            "esses",
            "essas",
            "aquilo",
            "ele",
            "ela",
            "eles",
            "elas",
            "metodo",
            "estrategia",
            "passo",
            "continua",
        }
        return any(t in contextual_terms for t in tokens)


_default_engine = ConversationRecoveryEngine()


def analyze_conversation_signal(
    message: str,
    last_topic: Optional[str] = None,
    memory: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return _default_engine.analyze(message=message, last_topic=last_topic, memory=memory)
