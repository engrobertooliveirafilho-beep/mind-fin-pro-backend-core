from app.humanization.universal_recovery_runtime import semantic_recovery
from app.runtime.identity_guard_runtime import guard_identity_fallback
from app.runtime.dialogue_state import (
    is_repeated,
    remember_response,
    short_message_type
)
from app.runtime.conversational_reasoning import (
    resolve_followup,
    update_dialogue_state
)
from app.runtime.visible_response_layer import visible_reformulate

def naturalize_response(answer: str, intent: dict, state: dict, autonomous: dict) -> str:
    user_id = state.get("user_id", "Roberto")
    name = "Roberto"
    focus = state.get("dominant_project", "MIND")
    msg = (state.get("last_unresolved_topic") or "").strip()
    msg_l = msg.lower()
    kind = short_message_type(msg)

    follow = resolve_followup(user_id, msg)
    if follow.get("resolved"):
        out = visible_reformulate(follow["answer"], msg, focus)
        remember_response(user_id, out)
        update_dialogue_state(user_id, msg, out)
        return out

    plan = autonomous.get("plan", {}).get("next_action", "avançar a próxima camada crítica")

    if kind == "greeting":
        out = f"Oi, {name}. Estou aqui. O contexto do {focus} continua aberto."
    elif kind == "ack":
        out = f"Fechado. Seguimos com o {focus} sem reiniciar contexto."
    elif kind == "repetition_complaint":
        out = "Você tem razão. Eu estava repetindo em vez de responder. Vou corrigir isso: a partir daqui, respondo a pergunta direta primeiro."
    elif any(x in msg_l for x in ["mas nao ta funcionando","não ta funcionando","nao está funcionando","não está funcionando","ainda nao arrumou","ainda não arrumou"]):
        out = "Você tem razão. O problema é que ela voltou para frase genérica em vez de continuar o contexto. O conserto é continuidade conversacional e bloqueio de repetição."
    elif "qual seria" in msg_l:
        out = "O gargalo é a memória curta da conversa. Ela precisa lembrar o contexto anterior e responder o follow-up sem voltar para frase genérica."
    elif any(x in msg_l for x in ["quem eh vc","quem é vc","quem é você","quem e voce","quem é voce"]):
        out = "Sou a Eldora do MIND. Converso com contexto e continuidade, sem resetar a conversa."
    elif any(x in msg_l for x in ["como vai me ajudar","como vc vai me ajudar","como você vai me ajudar","me ajuda em que"]):
        out = "Vou te ajudar de forma prática: organizar suas ideias, lembrar contexto, transformar conversa em plano, explicar conteúdos, priorizar decisões e executar próximos passos sem perder o fio da conversa."
    elif kind == "how_to":
        out = "Faça em três passos: preserve a última pergunta, gere uma resposta visível direta e só use detalhes técnicos quando o usuário pedir."
    elif kind == "continue":
        out = f"Vamos seguir no {focus}. O próximo passo é deixar a resposta externa mais direta, natural e menos autocentrada."
    elif "achou" in msg_l or "opinião" in msg_l:
        out = f"Eu achei que foi um avanço real, {name}. A base funciona; agora o desafio é fazer a Eldora conversar melhor."
    elif intent.get("intent") in ["project_execution", "continuity_request"]:
        out = f"{name}, sigo no {focus}. Próximo passo: {plan}."
    else:
        out = answer if "Diagnóstico:" not in answer else semantic_recovery(msg)

    if is_repeated(user_id, out):
        out = visible_reformulate(out, msg, focus)

    update_dialogue_state(
        user_id,
        msg,
        out,
        claim="melhorar resposta visível antes de novas camadas",
        reasoning=None,
        confidence=0.90
    )
    remember_response(user_id, out)
    return out







