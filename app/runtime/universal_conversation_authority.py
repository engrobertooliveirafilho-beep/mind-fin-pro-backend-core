from __future__ import annotations
from app.runtime.cognitive_conversation_runtime import decide_turn
from dataclasses import dataclass, asdict
from typing import Any, Dict, List


@dataclass
class ActiveConversationalObject:
    sender_id: str
    active_problem: str = "contexto ativo"
    reasoning_axis: str = "continuidade semântica"
    execution_axis: str = "próximo passo verificável"
    evidence_axis: str = "validação objetiva"
    last_user_goal: str = ""
    followup_depth: int = 1
    semantic_anchor: str = "active_context"
    continuity_score: float = 0.0


class UniversalConversationAuthority:
    def __init__(self):
        self.objects: Dict[str, ActiveConversationalObject] = {}

    def _intent(self, text: str) -> str:
        t = (text or "").lower()

        if any(x in t for x in [
            "dormi","sono","cansado","triste","ansioso"
        ]):
            return "emotional_safe"

        if any(x in t for x in ["passo a passo","como executar","roteiro"]):
            return "execute"

        if any(x in t for x in [
            "detalhe melhor",
            "aprofunde",
            "explique melhor",
            "ainda mais"
        ]):
            return "deepen"

        if any(x in t for x in [
            "validar","verificar","confirmar","testar"
        ]):
            return "validate"

        return "ask"

    def _abstract_problem(self, text: str) -> str:
        t = " ".join((text or "").split()).strip()
        return t[:120] if t else "contexto ativo"

    def build_context(
        self,
        sender_id: str,
        message: str,
        memory_context: List[str] | None = None
    ) -> Dict[str, Any]:

        intent = self._intent(message)
        prev = self.objects.get(sender_id)

        if prev and intent in ["deepen","execute","validate","emotional_safe"]:
            obj = prev
            obj.followup_depth = min(obj.followup_depth + 1, 5)
            obj.continuity_score = 0.95
            if intent == "emotional_safe":
                obj.semantic_anchor = "emotional_safe"
        else:
            obj = ActiveConversationalObject(
                sender_id=sender_id,
                active_problem=self._abstract_problem(message),
                reasoning_axis="causa prioridade dependência",
                execution_axis="transformar contexto em ação",
                evidence_axis="teste log evidência",
                last_user_goal=self._abstract_problem(message),
                followup_depth=1,
                continuity_score=0.70,
            )

        self.objects[sender_id] = obj

        return {
            "sender_id": sender_id,
            "active_intent": intent,
            "active_reasoning_mode": "universal_contextual_authority",
            "stage": (
                "execute"
                if intent == "execute"
                else "deepen"
            ),
            "depth_level": obj.followup_depth,
            "semantic_continuity": obj.continuity_score,
            "grounding_level": "contextual",
            "execution_need": intent == "execute",
            "social_energy": (
                "low"
                if intent == "emotional_safe"
                else "neutral"
            ),
            "conversational_budget": 220,
            "memory_context": memory_context or [],
            "aco": asdict(obj),
        }

    def render(
        self,
        ctx: Dict[str, Any],
        message: str
    ) -> str:

        t = (message or "").lower().strip()
        intent = ctx["active_intent"]
        aco = ctx["aco"]
        problem = aco["active_problem"]
        depth = int(ctx.get("depth_level", 1))

        emotional_text = (t + " " + str(problem).lower())
        emotional_signal = any(x in emotional_text for x in [
            "dormi","sono","cansado","triste","ansioso"
        ])

        if intent == "emotional_safe" or emotional_signal or aco.get("semantic_anchor") == "emotional_safe":
            return (
                "Detalhe útil: energia baixa pede redução de decisões, "
                "sono como prioridade e só tarefas essenciais hoje."
            )

        if intent == "execute" or "passo a passo" in t:
            return (
                f"Passo a passo: transformar {problem} "
                "em ação verificável, definir objetivo, "
                "executar menor ação, medir evidência e iterar."
            )

        if "detalhe melhor" in t:
            return (
                f"Cognição profunda: aprofundar {problem}, "
                "preservar continuidade contextual e evitar bleed semântico."
            )

        if "aprofunde" in t or "ainda mais" in t:

            if depth <= 2:
                return f"A causa aberta é {problem}. Próximo passo: isolar a falha, testar uma hipótese e registrar evidência."

            if depth == 3:
                return (
                    f"Cognição profunda: separar causa, prioridade, "
                    f"risco e evidência dentro de {problem}."
                )

            if depth == 4:
                return (
                    f"Aprofundamento estratégico: transformar {problem} "
                    "em critérios, dependências e trade-offs verificáveis."
                )

            return (
                f"Execução contextual: converter {problem} "
                "em sequência operacional sem bleed."
            )

        return (
            f"Continuidade contextual: manter foco em {problem}, "
            "sem reset semântico e sem fallback genérico."
        )


_ucca = UniversalConversationAuthority()


def build_universal_conversation_context(
    sender_id: str,
    message: str,
    memory_context: List[str] | None = None
) -> Dict[str, Any]:
    return _ucca.build_context(
        sender_id,
        message,
        memory_context
    )


def universal_conversation_reply(
    sender_id: str,
    message: str,
    memory_context: List[str] | None = None
) -> str:
    ctx = _ucca.build_context(
        sender_id,
        message,
        memory_context
    )
    return _ucca.render(
        ctx,
        message
    )[:ctx["conversational_budget"]]




