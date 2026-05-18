_DIALOGUE = {}

def get_dialogue_state(user_id: str) -> dict:
    return _DIALOGUE.get(user_id, {
        "last_user_message":"",
        "last_assistant_message":"",
        "last_topic":"MIND/Eldora",
        "last_claim":"melhorar conversa natural antes de novas camadas",
        "last_reasoning":"porque o runtime já funciona; o gargalo atual é qualidade de diálogo.",
        "confidence":0.86
    })

def update_dialogue_state(user_id: str, user_message: str, assistant_message: str, claim: str = "", reasoning: str = "", confidence: float = 0.86):
    prev = get_dialogue_state(user_id)
    _DIALOGUE[user_id] = {
        "last_user_message": user_message,
        "last_assistant_message": assistant_message,
        "last_topic": "MIND/Eldora",
        "last_claim": claim or prev.get("last_claim"),
        "last_reasoning": reasoning or prev.get("last_reasoning"),
        "confidence": confidence
    }
    return _DIALOGUE[user_id]

def classify_followup(message: str) -> str:
    t=(message or "").strip().lower()
    if t in ["porque?", "por que?", "pq?", "porque", "por que"]: return "causal"
    if t in ["certeza?", "tem certeza?", "certeza", "confirma?"]: return "confirmation"
    if "qual o melhor" in t or "qual a melhor" in t or t in ["qual?", "qual"]: return "comparison"
    if t.startswith("como"): return "how_to"
    return "none"

def resolve_followup(user_id: str, message: str) -> dict:
    state = get_dialogue_state(user_id)
    kind = classify_followup(message)

    if kind == "comparison":
        answer = "O melhor agora é melhorar a conversa natural e a qualidade conversacional, não criar mais infraestrutura. A base já está viva; o que limita a Eldora é responder com coerência curta, sem repetir e sem soar como relatório."
    elif kind == "causal":
        answer = f"Porque {state['last_reasoning']} Se eu continuar criando camada antes disso, só aumento complexidade em cima de uma conversa ainda rígida."
    elif kind == "confirmation":
        conf = int(state.get("confidence",0.86)*100)
        answer = f"Tenho {conf}% de confiança. A evidência é simples: quando você perguntou algo curto, ela ainda respondeu com frase genérica ou repetida. Então o gargalo é diálogo, não backend."
    elif kind == "how_to":
        answer = "Você faz isso criando uma janela curta de diálogo: última pergunta, última resposta, última afirmação e motivo. Aí 'porque?' e 'certeza?' deixam de ser mensagens soltas e passam a responder ao contexto."
    else:
        return {"resolved": False, "kind": kind, "answer": ""}

    update_dialogue_state(user_id, message, answer)
    return {"resolved": True, "kind": kind, "answer": answer}

