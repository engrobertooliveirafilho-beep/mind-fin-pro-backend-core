import json
from pathlib import Path

def enrich_context(message: str):
    context = []

    if "plano" in message:
        context.append("strategy_layer")

    if "lançar" in message:
        context.append("launch_domain")

    return {
        "message": message,
        "memory_context": context
    }
