from app.runtime.dialogue_state import is_repeated, remember_response, short_message_type

def naturalize_response(answer: str, intent: dict, state: dict, autonomous: dict) -> str:
    user_id = state.get("user_id", "Roberto")
    name = "Roberto"
    focus = state.get("dominant_project", "MIND")
    msg = (state.get("last_unresolved_topic") or "").strip()
    msg_l = msg.lower()
    kind = short_message_type(msg)
    plan = autonomous.get("plan", {}).get("next_action", "avançar a próxima camada crítica")

    if kind == "greeting":
        out = f"Oi, {name}. Estou com o contexto do {focus} aberto. Podemos seguir da evolução da Eldora ou atacar o próximo gargalo."
    elif kind == "ack":
        out = f"Fechado. Mantive o contexto ativo: {focus}, Eldora e próximo passo P1."
    elif kind == "repetition_complaint":
        out = "Você tem razão. Eu estava repetindo porque a camada de naturalização estava usando um template fixo. O ajuste agora é variar a resposta pela intenção real e bloquear repetição."
    elif kind == "how_to":
        out = f"Você faz isso em três cortes: primeiro bloqueia repetição, depois cria respostas curtas para conversa simples, e por último deixa o plano autônomo entrar só quando a pergunta pedir execução."
    elif kind == "continue":
        out = f"Vamos seguir. O próximo passo é {plan}, mas sem repetir o mesmo texto: agora a prioridade é melhorar variação e conversa natural."
    elif "achou" in msg_l or "opinião" in msg_l:
        out = f"Eu achei um avanço real, {name}. A base técnica está funcionando; o problema agora é refinamento de comportamento, não infraestrutura."
    elif intent.get("intent") in ["project_execution", "continuity_request"]:
        out = f"{name}, sigo no {focus}. Próximo passo: {plan}. Vou manter execução, mas com menos rigidez na conversa."
    else:
        out = answer if "Diagnóstico:" not in answer else f"{name}, entendi. Vou manter o contexto do {focus} e responder sem voltar para template."

    if is_repeated(user_id, out):
        out = f"Vou reformular: o ponto central é manter o {focus} avançando sem cair em resposta repetida. A próxima ação continua sendo {plan}, mas agora com diálogo mais natural."

    remember_response(user_id, out)
    return out
