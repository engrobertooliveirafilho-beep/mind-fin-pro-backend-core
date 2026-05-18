from app.runtime.dialogue_state import (
    is_repeated,
    remember_response,
    short_message_type
)

from app.runtime.conversational_reasoning import (
    resolve_followup,
    update_dialogue_state
)

def naturalize_response(answer: str, intent: dict, state: dict, autonomous: dict) -> str:

    user_id = state.get("user_id", "Roberto")
    name = "Roberto"

    focus = state.get("dominant_project", "MIND")

    msg = (
        state.get("last_unresolved_topic")
        or ""
    ).strip()

    msg_l = msg.lower()

    kind = short_message_type(msg)

    follow = resolve_followup(user_id, msg)

    if follow.get("resolved"):
        remember_response(user_id, follow["answer"])
        return follow["answer"]

    plan = autonomous.get(
        "plan",
        {}
    ).get(
        "next_action",
        "avançar a próxima camada crítica"
    )

    if kind == "greeting":

        out = (
            f"Oi, {name}. "
            f"Estou com o contexto do {focus} aberto. "
            f"Podemos seguir da evolução da Eldora "
            f"ou atacar o próximo gargalo."
        )

    elif kind == "ack":

        out = (
            f"Fechado. "
            f"Mantive o contexto ativo: {focus}, "
            f"Eldora e prioridade atual."
        )

    elif kind == "repetition_complaint":

        out = (
            "Você tem razão. "
            "Eu estava repetindo porque a camada "
            "de naturalização usava um template fixo. "
            "Agora estou separando follow-up, "
            "contexto e intenção real."
        )

    elif kind == "how_to":

        out = (
            "Você resolve isso criando memória curta "
            "de diálogo, bloqueio de repetição "
            "e respostas diferentes para perguntas "
            "causais, confirmação e comparação."
        )

    elif kind == "continue":

        out = (
            f"Vamos seguir no {focus}. "
            f"O próximo passo é {plan}, "
            f"mas agora priorizando conversa natural "
            f"e coerência contextual."
        )

    elif "achou" in msg_l or "opinião" in msg_l:

        out = (
            f"Eu achei um avanço real, {name}. "
            f"A infraestrutura já funciona; "
            f"o gargalo agora é comportamento conversacional."
        )

    elif intent.get("intent") in [
        "project_execution",
        "continuity_request"
    ]:

        out = (
            f"{name}, sigo no {focus}. "
            f"Próximo passo: {plan}. "
            f"Vou manter execução "
            f"sem cair em resposta mecânica."
        )

    else:

        out = (
            answer
            if "Diagnóstico:" not in answer
            else (
                f"{name}, entendi. "
                f"Vou responder mantendo "
                f"o contexto do {focus} "
                f"sem voltar para template."
            )
        )

    if is_repeated(user_id, out):

        out = (
            f"Vou responder diferente: "
            f"o foco agora é melhorar "
            f"a qualidade da conversa "
            f"da Eldora sem perder "
            f"continuidade do {focus}."
        )

    update_dialogue_state(
        user_id,
        msg,
        out,
        claim="melhorar conversa natural antes de novas camadas",
        reasoning="o backend, WhatsApp, memória, RAG e LLM já estão operacionais; o gargalo atual é qualidade conversacional.",
        confidence=0.86
    )

    remember_response(user_id, out)

    return out
