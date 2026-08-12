def route_intent(message: str, memory=None):
    t = (message or "").lower()

    # MEMORY BOOST (CRITICAL ADDITION)
    memory_flags = []
    if memory:
        memory_flags = memory.get("memory_flags", [])

    # augment message with memory signals
    t = t + " " + " ".join(memory_flags)

    mapping = [
        ("study_deep_dive",["estudar","aula","aprofundar","explica"]),
        ("strategic_planning",["estratégia","plano","prioridade","80/20","launch_domain","strategy_mode"]),
        ("emotional_presence",["triste","ansioso","sozinho","desanimado"]),
        ("project_execution",["executar","implantar","prosseguir","deploy"]),
        ("visual_identity",["rosto","aparência","persona visual","imagem"]),
        ("technical_debug",["erro","traceback","bug","falhou"]),
        ("market_research",["mercado","concorrente","pesquisa"]),
        ("correction_request",["corrigir","não era isso","desvio"]),
        ("continuity_request",["continua","prosseguir","retomar"])
    ]

    for intent, keys in mapping:
        if any(k in t for k in keys):
            return {
                "intent": intent,
                "confidence": 0.92,
                "depth_required": "high",
                "response_mode": "structured",
                "needs_memory": True,
                "needs_state_update": True
            }

    return {
        "intent": "casual_context",
        "confidence": 0.70,
        "depth_required": "medium",
        "response_mode": "direct",
        "needs_memory": True,
        "needs_state_update": True
    }
