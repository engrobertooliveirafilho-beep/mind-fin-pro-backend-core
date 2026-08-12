import json

from app.eldora.intelligence.llm_live import generate_llm_response


def _safe_json(value):
    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            default=str,
        )
    except Exception:
        return str(value)


def _context(intent, memory, internal_state, persona_context, strategy):

    return (
        "CONTEXTO INTERNO ELDORA\n"
        + _safe_json({
            "intent": intent or {},
            "memory": memory or {},
            "state": internal_state or {},
            "persona": persona_context or {},
            "strategy": strategy or {},
        })
        + "\n\n"
        + "REGRAS\n"
        + "- Responda diretamente à mensagem atual.\n"
        + "- Use memória apenas se for relevante ao assunto atual.\n"
        + "- Se o assunto mudou, siga o novo assunto.\n"
        + "- Não exponha runtime, módulos, MIND, scores ou arquitetura.\n"
        + "- Não use templates técnicos.\n"
        + "- Não invente contexto ausente.\n"
        + "- Seja natural, útil e contextual.\n"
        + "- Pergunte apenas quando necessário.\n"
    )


class ResponseBuilder:

    def __init__(self, *args, **kwargs):
        self.version = "real_llm_v1"

    def build(
        self,
        user_message="",
        intent=None,
        memory=None,
        internal_state=None,
        persona_context=None,
        strategy=None,
    ):

        return build_response(
            user_message,
            intent or {"intent": "general"},
            memory or {},
            internal_state or {},
            persona_context or {},
            strategy or {},
        )

    def build_response(self, *args, **kwargs):
        return self.build(*args, **kwargs)


def build_response(
    user_message,
    intent,
    memory,
    internal_state,
    persona_context,
    strategy,
):

    message = str(user_message or "").strip()

    if not message:
        return ""

    intent_name = (
        intent.get("intent", "general")
        if isinstance(intent, dict)
        else "general"
    )

    result = generate_llm_response(
        prompt=message,
        context=_context(
            intent,
            memory,
            internal_state,
            persona_context,
            strategy,
        ),
        intent=intent_name,
    )

    if not isinstance(result, dict):
        return ""

    if not result.get("llm_real_used"):
        return ""

    answer = str(
        result.get("answer")
        or ""
    ).strip()

    if not answer:
        return ""

    forbidden = (
        "fallback eldora ativo",
        "sem openai_api_key",
        "diagnóstico: entendi a intenção",
        "resumo técnico do mind",
        "runtime estável",
    )

    low = answer.lower()

    if any(x in low for x in forbidden):
        return ""

    return answer