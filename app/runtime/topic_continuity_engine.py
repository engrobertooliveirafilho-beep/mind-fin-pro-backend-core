FOLLOWUP_WORDS = {
    "aprofunde","aprofundar","continue","continua","continue isso",
    "explique mais","detalhe","mais detalhes","sobre isso",
    "e os pontos fracos","e manutenção","e consumo","vale a pena"
}

def resolve_followup(message:str, session_ctx:dict):
    msg=(message or "").strip().lower()
    last_topic=(session_ctx or {}).get("last_topic")

    if msg in FOLLOWUP_WORDS and last_topic:
        return {"followup":True,"topic":last_topic}

    if "k1300" in msg or "bmw k1300" in msg:
        session_ctx["last_topic"]="BMW_K1300_BUYING"

    return {"followup":False,"topic":session_ctx.get("last_topic")}
