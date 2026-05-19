from collections import defaultdict, deque
import re

STATE = defaultdict(lambda: {
    "turns": deque(maxlen=20),
    "active_topic": "",
    "previous_topic": "",
    "conversation_goal": "",
    "open_questions": [],
    "recent_entities": [],
    "last_user_intent": "",
    "last_assistant_intent": "",
    "continuity_confidence": 0.0
})

REF = re.compile(
    r"\b(isso|esse|agora|e ai|e aí|como ficou|sentiu diferença|qual score|e depois)\b",
    re.I
)

TOPICS = {
    "implant": "implantações eldora",
    "implantações": "implantações eldora",
    "implantacoes": "implantações eldora",
    "human": "humanização eldora",
    "humanizada": "humanização eldora",
    "score": "score humanização",
    "carro": "carros",
    "carros": "carros",
    "diesel": "motor diesel"
}

def infer_topic(text, previous_topic=""):
    t = (text or "").lower().strip()

    # prioridade máxima: palavra explícita
    for key, topic in TOPICS.items():
        if key in t:
            return topic

    # referência implícita ("isso", "agora", etc.)
    if REF.search(t) and previous_topic:
        return previous_topic

    return previous_topic or "conversa_geral"


def update(sender_id, user_message, assistant_message=""):
    state = STATE[sender_id]

    previous = state.get("active_topic", "")

    current = infer_topic(user_message, previous)

    state["previous_topic"] = previous
    state["active_topic"] = current

    state["turns"].append({
        "user": user_message,
        "assistant": assistant_message
    })

    state["continuity_confidence"] = 0.95 if previous else 0.75

    return state


def get(sender_id):
    return STATE[sender_id]
