import random, uuid

PERSONAS=[
 "executive_impatient","emotional_user","technical_engineer","confused_beginner",
 "skeptical_high_iq","small_business_owner","farmer_haras_owner","pet_owner",
 "car_enthusiast","quiet_user","angry_user","anxious_user","casual_friend",
 "low_context_user","followup_heavy_user","typo_noisy_user"
]

TOPICS=[
 "eldora_runtime","humanizacao","cane_corso","automotivo","haras",
 "marketing","negocios","whatsapp","memoria","smalltalk","erro_tecnico"
]

SCENARIOS=[
 ("executive_impatient","eldora_runtime","direto: isso já funciona ou ainda tá quebrado?"),
 ("emotional_user","humanizacao","cara, tá difícil acertar isso, né?"),
 ("technical_engineer","erro_tecnico","qual camada está vazando contexto no webhook?"),
 ("confused_beginner","whatsapp","não entendi, por que respondeu duas vezes?"),
 ("skeptical_high_iq","memoria","prove que você lembra o assunto certo sem inventar"),
 ("small_business_owner","negocios","isso ajuda a vender ou é só tecnologia bonita?"),
 ("farmer_haras_owner","haras","como organizo piquete, baia e rotina dos animais?"),
 ("pet_owner","cane_corso","como escolho um filhote de cane corso saudável?"),
 ("car_enthusiast","automotivo","diesel é melhor que gasolina para torque?"),
 ("typo_noisy_user","smalltalk","bom dia, td bemw?"),
 ("followup_heavy_user","humanizacao","e agora? sentiu diferença? ainda nada?"),
 ("angry_user","eldora_runtime","de novo isso errado? arruma logo"),
 ("anxious_user","erro_tecnico","será que estragou tudo?"),
 ("casual_friend","smalltalk","oi, como tá por aí?"),
 ("low_context_user","memoria","isso aí, continua"),
]

def simulate_reply(user_text, persona, topic):
    t=(user_text or "").lower()
    if topic=="eldora_runtime" or "webhook" in t or "camada" in t:
        return "o ponto principal está no roteamento: intenção curta, memória e fallback precisam obedecer uma ordem única."
    if topic=="humanizacao":
        return "melhorou, mas ainda precisa reduzir resposta genérica e manter continuidade do assunto."
    if topic=="cane_corso":
        return "para Cane Corso, priorize genética, exames dos pais, temperamento e socialização desde cedo."
    if topic=="automotivo":
        return "diesel tende a entregar mais torque por compressão alta e eficiência em baixa rotação."
    if topic=="haras":
        return "o ideal é separar fluxo, drenagem, sombra, água limpa e manejo diário dos animais."
    if topic=="smalltalk":
        return "tudo certo por aqui."
    return "Vou seguir pelo contexto atual, sem reiniciar a conversa."

def score(user_text, answer, persona, topic):
    penalty=0
    low=(answer or "").lower()
    bad=["como posso ajudar","me dê mais detalhes","sou a eldora","prova","matemática","runtime estável v2"]
    penalty+=sum(12 for b in bad if b in low)
    if topic=="smalltalk" and len(answer)>80: penalty+=8
    if persona in ["executive_impatient","angry_user"] and len(answer)>180: penalty+=10
    return max(0,min(100,96-penalty))

def generate_episode(i):
    persona,topic,user=random.choice(SCENARIOS)
    answer=simulate_reply(user,persona,topic)
    return {
        "episode_id":str(uuid.uuid4()),
        "sender_id":"swarm_simulation",
        "kind":"simulation",
        "persona":persona,
        "theme":topic,
        "user_message":user,
        "assistant_answer":answer,
        "humanization_score":score(user,answer,persona,topic)
    }

