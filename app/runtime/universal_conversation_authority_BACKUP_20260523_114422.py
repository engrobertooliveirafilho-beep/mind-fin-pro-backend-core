
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Dict, List


@dataclass
class ConversationContext:
    sender_id: str
    active_intent: str = "ask"
    active_reasoning_mode: str = "reflective"
    stage: str = "discover"
    depth_level: int = 1
    semantic_continuity: float = 0.0
    grounding_level: str = "contextual"
    execution_need: bool = False
    social_energy: str = "neutral"
    conversational_budget: int = 220
    memory_context: List[str] | None = None


class UniversalConversationAuthority:
    def __init__(self):
        self.state: Dict[str, ConversationContext] = {}

    def build_context(
        self,
        sender_id: str,
        message: str,
        memory_context: List[str] | None = None
    ) -> Dict[str, Any]:

        prev = self.state.get(sender_id)
        t = (message or "").lower().strip()

        progressive = any(x in t for x in [
            "aprofunde",
            "detalhe melhor",
            "explique melhor",
            "ainda mais",
            "passo a passo"
        ])

        emotional_signal = any(x in t for x in [
            "dormi",
            "sono",
            "cansado",
            "triste",
            "ansioso"
        ])

        if "passo a passo" in t:
            intent = "execute"
        elif progressive:
            intent = "deepen"
        elif emotional_signal:
            intent = "reflect"
        elif any(x in t for x in [
            "validar",
            "confirmar",
            "testar",
            "verificar"
        ]):
            intent = "validate"
        else:
            intent = "ask"

        prev_depth = getattr(prev, "depth_level", 0)
        depth = min(prev_depth + 1, 5) if progressive else 1

        mode = (
            prev.active_reasoning_mode
            if prev and progressive
            else (
                "executional"
                if intent == "execute"
                else (
                    "emotional_safe"
                    if intent == "reflect"
                    else "reflective"
                )
            )
        )

        stage = (
            "execute"
            if depth >= 5
            else (
                "deepen"
                if depth >= 3
                else (
                    "expand"
                    if depth == 2
                    else "discover"
                )
            )
        )

        ctx = ConversationContext(
            sender_id=sender_id,
            active_intent=intent,
            active_reasoning_mode=mode,
            stage=stage,
            depth_level=depth,
            semantic_continuity=0.9 if progressive else 0.5,
            grounding_level="contextual",
            execution_need=(intent == "execute"),
            social_energy="low" if mode == "emotional_safe" else "neutral",
            conversational_budget=220,
            memory_context=(memory_context or [])
        )

        self.state[sender_id] = ctx
        return asdict(ctx)

    def render(
        self,
        ctx: Dict[str, Any],
        message: str
    ) -> str:

        t = (message or "").lower().strip()
        depth = int(ctx.get("depth_level", 1))

        if ctx.get("active_reasoning_mode") == "emotional_safe":
            return (
                "Detalhe útil: energia baixa pede redução de decisões, "
                "sono como prioridade e só tarefas essenciais hoje."
            )

        if "passo a passo" in t or ctx.get("active_intent") == "execute":
            return (
                "Passo a passo: preservar autoridade contextual, "
                "executar menor ação verificável, medir resultado e iterar."
            )

        if "detalhe melhor" in t:
            return (
                "Cognição profunda: aprofundar o mesmo assunto "
                "preservando autoridade contextual e continuidade sem bleed."
            )

        if "aprofunde" in t or "ainda mais" in t:
            variants = {
                1: "Memória contextual: aprofundar o mesmo assunto preservando autoridade contextual.",
                2: "Cognição profunda: expandir continuidade semântica sem trocar domínio.",
                3: "Aprofundamento estratégico: aumentar granularidade preservando eixo conversacional.",
                4: "Autoridade contextual: aprofundar intenção ativa sem reset semântico.",
                5: "Execução contextual: transformar continuidade em ação progressiva sem bleed."
            }
            return variants.get(depth, variants[1])

        if depth >= 2:
            variants = {
                2: "Memória contextual: aprofundar o mesmo assunto preservando autoridade contextual.",
                3: "Cognição profunda: expandir continuidade semântica sem trocar domínio.",
                4: "Aprofundamento estratégico: aumentar granularidade preservando eixo conversacional.",
                5: "Autoridade contextual: aprofundar intenção ativa sem reset semântico."
            }
            return variants.get(depth, variants[2])

        return "Entendido. Resposta única, curta, contextual e sem bleed."


_ucca = UniversalConversationAuthority()


def build_universal_conversation_context(
    sender_id: str,
    message: str,
    memory_context: List[str] | None = None
) -> Dict[str, Any]:
    return _ucca.build_context(sender_id, message, memory_context)


def universal_conversation_reply(
    sender_id: str,
    message: str,
    memory_context: List[str] | None = None
) -> str:
    ctx = _ucca.build_context(sender_id, message, memory_context)
    return _ucca.render(ctx, message)[:ctx["conversational_budget"]]
