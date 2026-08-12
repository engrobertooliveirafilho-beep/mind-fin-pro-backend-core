def inject_memory(message: str):
    context = []

    if "lançar" in message:
        context.append("launch_domain")

    if "plano" in message:
        context.append("strategy_mode")

    if "risco" in message:
        context.append("risk_simulation")

    return {
        "message": message,
        "memory_flags": context
    }
