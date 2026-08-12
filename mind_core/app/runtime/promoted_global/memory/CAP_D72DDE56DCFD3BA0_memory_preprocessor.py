def inject_memory(message: str):
    context = []

    if "lançar" in message:
        context.append("launch_domain")

    if "plano" in message:
        context.append("strategy_mode")

    if "risco" in message:
        context.append("risk_simulation")

    # IMPORTANT: return STRUCTURED CONTEXT, not string append
    return {
        "original_message": message,
        "memory_flags": context,
        "enhanced_intent_hint": "strategic_planning" if "plano" in message else None
    }
