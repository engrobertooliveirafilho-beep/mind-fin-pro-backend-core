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
        intent = "execute" if any(x in t for x in ["passo a passo","roteiro","plano operacional","como executar"]) else "deepen" if any(x in t for x in ["aprofunde","detalhe melhor","explique melhor","ainda mais"]) else "validate" if any(x in t for x in ["validar","verificar","confirmar","testar"]) else "reflect" if any(x in t for x in ["nÃ£o dormi","cansado","mal hoje","triste","ansioso"]) else "ask"
        depth = 5 if intent == "execute" else min(5, max((prev.depth_level + 1 if prev else 2), 3)) if intent == "deepen" else 1
        mode = "executional" if intent == "execute" else "emotional_safe" if intent == "reflect" else "decision_support" if intent == "validate" else (prev.active_reasoning_mode if prev and intent == "deepen" else "reflective")
        stage = "execute" if depth >= 5 else "deepen" if depth >= 3 else "expand" if depth == 2 else "discover"
        ctx = ConversationContext(sender_id, intent, mode, stage, depth, 0.75 if prev else 0.0, "contextual", intent == "execute", "low" if mode == "emotional_safe" else "neutral", 220, memory_context or [])
        self.state[sender_id] = ctx
        return asdict(ctx)

    def render(self, ctx: Dict[str, Any], message: str) -> str:
        if ctx["active_intent"] == "execute":
            return "Passo a passo: definir objetivo, preservar contexto, executar menor aÃ§Ã£o verificÃ¡vel, medir falha e fechar com evidÃªncia."
        if ctx["active_reasoning_mode"] == "emotional_safe":
            return "Detalhe Ãºtil: energia baixa pede reduÃ§Ã£o de decisÃµes, sono como prioridade e sÃ³ tarefas essenciais hoje."
        if ctx["depth_level"] >= 4:
            return "Aprofundando: preserve o contexto ativo, aumente profundidade e avance sem puxar categorias de conversas anteriores."
        if ctx["depth_level"] >= 3:
            return "Detalhe: aprofunde o mesmo assunto, mantenha intenÃ§Ã£o atual e bloqueie troca semÃ¢ntica automÃ¡tica."
        return "Entendido. Resposta Ãºnica, curta, contextual e sem bleed."

_ucca = UniversalConversationAuthority()

def build_universal_conversation_context(sender_id: str, message: str, memory_context: List[str] | None = None) -> Dict[str, Any]:
    return _ucca.build_context(sender_id, message, memory_context)

def universal_conversation_reply(sender_id: str, message: str, memory_context: List[str] | None = None) -> str:
    ctx = _ucca.build_context(sender_id, message, memory_context)
    return _ucca.render(ctx, message)[:ctx["conversational_budget"]]
