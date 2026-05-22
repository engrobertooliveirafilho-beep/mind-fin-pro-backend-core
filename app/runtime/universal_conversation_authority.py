
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Dict, List
import re

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

    def build_context(self, sender_id: str, message: str, memory_context: List[str] | None = None) -> Dict[str, Any]:
        prev = self.state.get(sender_id)
        t = message.lower().strip()
        progressive = any(x in t for x in ["aprofunde", "detalhe melhor", "explique melhor", "ainda mais"])
        emotional_signal = any(x in t for x in ["dormi", "sono", "cansado", "cansada", "mal hoje", "triste", "ansioso", "ansiosa"])
        intent = "execute" if any(x in t for x in ["passo a passo", "roteiro", "plano operacional", "como executar"]) else "deepen" if progressive else "validate" if any(x in t for x in ["validar", "verificar", "confirmar", "testar"]) else "reflect" if emotional_signal else "ask"
        depth = 5 if intent == "execute" else min(5, max((prev.depth_level + 1 if prev else 2), 3)) if intent == "deepen" else 1
        if prev and progressive:
            mode = prev.active_reasoning_mode
        else:
            mode = "executional" if intent == "execute" else "emotional_safe" if intent == "reflect" else "decision_support" if intent == "validate" else "reflective"
        stage = "execute" if depth >= 5 else "deepen" if depth >= 3 else "expand" if depth == 2 else "discover"
        ctx = ConversationContext(sender_id, intent, mode, stage, depth, 0.75 if prev else 0.0, "contextual", intent == "execute", "low" if mode == "emotional_safe" else "neutral", 220, memory_context or [])
        self.state[sender_id] = ctx
        return asdict(ctx)

    def render(self, ctx: Dict[str, Any], message: str) -> str:
        if ctx["active_reasoning_mode"] == "emotional_safe":
            return "Detalhe útil: energia baixa pede redução de decisões, sono como prioridade e só tarefas essenciais hoje."
        if ctx["active_intent"] == "execute":
            return "Passo a passo: definir objetivo, preservar contexto, executar menor ação verificável, medir falha e fechar com evidência."
        if ctx["depth_level"] >= 4:
            return "Cognição profunda: preserve o contexto ativo, aumente profundidade e avance sem puxar categorias de conversas anteriores."
        if ctx["depth_level"] >= 3:
            return "Memória contextual: aprofunde o mesmo assunto, mantenha intenção atual e bloqueie troca semântica automática."
        return "Entendido. Resposta única, curta, contextual e sem bleed."

_ucca = UniversalConversationAuthority()

def build_universal_conversation_context(sender_id: str, message: str, memory_context: List[str] | None = None) -> Dict[str, Any]:
    return _ucca.build_context(sender_id, message, memory_context)

def universal_conversation_reply(sender_id: str, message: str, memory_context: List[str] | None = None) -> str:
    ctx = _ucca.build_context(sender_id, message, memory_context)
    return _ucca.render(ctx, message)[:ctx["conversational_budget"]]
