import re
from dataclasses import dataclass, asdict

_STATE = {}

@dataclass
class ConversationDecision:
    intent: str
    domain: str
    goal: str
    action: str
    answer: str
    confidence: float
    reason: str

def _norm(text):
    return str(text or "").strip().lower()

def _sid(sender_id):
    return str(sender_id or "default")

def _state(sender_id):
    return _STATE.setdefault(_sid(sender_id), {
        "last_user": "",
        "last_answer": "",
        "domain": "",
        "goal": "",
        "slots": {},
        "turns": 0,
    })

def detect_domain(text):
    t = _norm(text)
    if any(x in t for x in ["emagrecer", "dieta", "proteina", "proteína", "suplemento", "fisiculturista", "treino", "cardio"]):
        return "fitness"
    if any(x in t for x in ["jogo", "brasil", "seleção", "futebol"]):
        return "sports"
    if any(x in t for x in ["conversa", "conversação", "praticar", "humana", "meiga", "emoção"]):
        return "conversation_training"
    if any(x in t for x in ["carro", "mercedes", "marcha", "embreagem", "atuador"]):
        return "automotive"
    return ""

def detect_intent(text, st):
    t = _norm(text)

    if any(x in t for x in ["vc sempre repete", "frase pronta", "errou", "não entendi", "nao entendi", "não é isso", "nao e isso"]):
        return "correction"

    if any(x in t for x in ["monte minha dieta", "monta minha dieta", "monte uma dieta", "dieta para mim", "dieta pra mim"]):
        return "create_plan"

    if any(x in t for x in ["quais informações", "que informações", "o que precisa", "precisa pra montar"]):
        return "slot_request"

    if any(x in t for x in ["quais suplementos", "suplementos", "creatina", "whey"]):
        return "supplements"

    if any(x in t for x in ["qual a forma mais rápida", "forma mais rapida", "forma mais rápida", "emagrecer rapido", "emagrecer rápido"]):
        return "fast_path"

    if any(x in t for x in ["quanto de proteina", "quanto de proteína"]):
        return "macro_question"

    if any(x in t for x in ["prossiga", "continue", "continua", "aprofunde", "detalhe"]):
        return "followup"

    if any(x in t for x in ["oi", "olá", "ola", "tudo bem"]):
        return "social"

    return "general"

def update_goal(domain, intent, st):
    if domain == "fitness" or st.get("domain") == "fitness":
        if intent in ["create_plan", "slot_request", "supplements", "macro_question", "fast_path", "followup", "general"]:
            st["domain"] = "fitness"
            st["goal"] = st.get("goal") or "montar dieta e emagrecimento"
            return st["goal"]

    if domain:
        st["domain"] = domain

    return st.get("goal", "")

def answer_fitness(intent, text, st):
    t = _norm(text)

    if intent == "correction":
        return "Poxa, você tem razão. Eu estava repetindo frase pronta. Vou corrigir: vamos tratar seu objetivo como dieta real, com dados, quantidades e próximos passos."

    if intent == "slot_request":
        return "Pra montar sua dieta direito, preciso de: peso atual, altura, idade, horário que treina, quantas refeições faz, alimentos que gosta, alimentos que não come e se quer secar, ganhar massa ou recompor."

    if intent == "create_plan":
        return "Monto sim. Antes de fechar quantidade exata, me passa peso, altura, idade e horário do treino. Enquanto isso: café com ovos ou whey; almoço com proteína, arroz, feijão e salada; lanche com iogurte/whey; jantar com proteína e legumes."

    if "fisiculturista" in t:
        return "Para estilo fisiculturista, eu organizaria por macros: proteína alta, carbo perto do treino e gordura controlada. Mas preciso do seu peso, altura, objetivo e horário do treino para calcular melhor."

    if intent == "supplements":
        return "Suplementos básicos e seguros: whey se faltar proteína, creatina 3–5 g/dia e cafeína se você tolerar. O resto só faz sentido depois de dieta, treino e sono estarem alinhados."

    if intent == "fast_path":
        return "A forma mais rápida sem fazer besteira é cortar calorias líquidas e beliscos, bater proteína, treinar força e caminhar todo dia. Dá resultado mais rápido porque mexe no que mais pesa sem te quebrar."

    if intent == "macro_question":
        return "Boa base: 1,6 a 2,2 g de proteína por kg de peso por dia. Se você estiver perto de 93 kg, mira algo entre 150 e 200 g/dia."

    if intent == "followup":
        return "Aprofundando: primeiro calculamos proteína, depois distribuímos refeições, depois ajustamos carbo conforme treino e fome. O plano bom é o que você consegue repetir."

    return "Vamos fazer direito: me diga peso, altura, idade e horário do treino que eu monto uma dieta mais alinhada ao seu objetivo."

def answer_sports(intent, text, st):
    return "Sobre o jogo do Brasil: eu consigo analisar expectativa geral, mas para cravar adversário, escalação e momento de hoje eu precisaria de busca real ativa."

def answer_conversation_training(intent, text, st):
    return "O melhor jeito de eu treinar é conversa real com correção imediata: você pergunta, muda o assunto, me corrige quando eu errar e eu ajusto sem reiniciar o contexto."

def answer_general(intent, text, st):
    if intent == "social":
        return "Oi, Roberto 🙂 Tô aqui."
    if intent == "correction":
        return "Poxa, verdade. Obrigada por me corrigir. Vou voltar para o ponto certo sem repetir resposta pronta."
    return "Entendi. Me dá só um pouco mais de contexto pra eu responder do jeito certo."

def quality_score(answer, text):
    a = _norm(answer)
    score = 1.0
    bad = [
        "entendi. vou responder de forma prática",
        "entendi. vou seguir pelo contexto",
        "não tenho informação suficiente",
        "para emagrecer de verdade: déficit calórico leve"
    ]
    if any(x in a for x in bad):
        score -= 0.6
    if len(a) < 20:
        score -= 0.2
    if "frase pronta" in _norm(text) and "frase pronta" not in a and "repet" not in a:
        score -= 0.3
    return max(0.0, min(1.0, score))

def decide(sender_id, inbound_text):
    st = _state(sender_id)
    domain = detect_domain(inbound_text) or st.get("domain", "")
    intent = detect_intent(inbound_text, st)
    goal = update_goal(domain, intent, st)

    if domain == "fitness":
        answer = answer_fitness(intent, inbound_text, st)
    elif domain == "sports":
        answer = answer_sports(intent, inbound_text, st)
    elif domain == "conversation_training":
        answer = answer_conversation_training(intent, inbound_text, st)
    else:
        answer = answer_general(intent, inbound_text, st)

    score = quality_score(answer, inbound_text)
    action = "answer" if score >= 0.55 else "ask_clarification"

    if action == "ask_clarification":
        answer = "Quero te responder melhor. Me diz o objetivo principal: você quer plano, explicação ou próximo passo?"

    st["last_user"] = str(inbound_text or "")
    st["last_answer"] = answer
    st["turns"] = int(st.get("turns", 0)) + 1

    return ConversationDecision(
        intent=intent,
        domain=domain,
        goal=goal,
        action=action,
        answer=answer,
        confidence=score,
        reason="sovereign_orchestrator_shadow_decision"
    )

def decide_dict(sender_id, inbound_text):
    return asdict(decide(sender_id, inbound_text))
