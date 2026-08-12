import json
from pathlib import Path

GRAPH_PATH = Path("_evidence/latest_graph.json")

# fallback safe loader
if GRAPH_PATH.exists():
    graph = json.loads(GRAPH_PATH.read_text())
else:
    graph = {"layers": {}, "total_files": 0}

def enrich_context(message: str):
    context = []

    if "estratégia" in message or "plano" in message:
        context.append("strategy_layer")

    if "lançar" in message or "Eldora" in message:
        context.append("launch_domain")

    if graph.get("layers", {}).get("runtime", 0) > 0:
        context.append("runtime_memory_available")

    return {
        "message": message,
        "memory_context": context,
        "graph_summary": graph
    }
