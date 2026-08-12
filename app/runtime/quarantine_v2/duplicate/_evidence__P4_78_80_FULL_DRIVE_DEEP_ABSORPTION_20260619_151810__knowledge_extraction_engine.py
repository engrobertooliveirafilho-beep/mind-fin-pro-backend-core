import json
import re
from pathlib import Path
from datetime import datetime, timezone

EXTRACTION_DIR = Path("runtime/knowledge_extraction")
EXTRACTION_DIR.mkdir(parents=True, exist_ok=True)

CATEGORIES = {
    "CAPABILITY": [
        "capability", "capacidade", "módulo", "modulo", "engine", "provider", "runtime",
        "retrieval", "memory", "router", "pipeline", "orchestrator"
    ],
    "ALGORITHM": [
        "algoritmo", "algorithm", "score", "ranking", "classificar", "classificação",
        "rerank", "embedding", "similaridade", "cosine", "pgvector"
    ],
    "ARCHITECTURE": [
        "arquitetura", "architecture", "fluxo", "pipeline", "camada", "layer",
        "kernel", "core", "orquestrador", "orchestrator"
    ],
    "BUG_FIX": [
        "erro", "bug", "fix", "corrigir", "falha", "traceback", "exception",
        "module not found", "indentationerror", "typeerror", "parsererror"
    ],
    "LESSON_LEARNED": [
        "lição", "licao", "aprendizado", "lesson", "aprendido", "não repetir",
        "evitar", "causa raiz", "root cause"
    ],
    "UNIMPLEMENTED_IDEA": [
        "ideia", "idéia", "falta", "pendente", "não implementado", "nao implementado",
        "precisa criar", "deve criar", "próximo", "proximo", "backlog"
    ],
    "INCOMPLETE_FEATURE": [
        "incompleto", "parcial", "não integrado", "nao integrado", "órfão", "orfao",
        "fora do pipeline", "sem uso", "pendente integração"
    ],
    "DEPENDENCY": [
        "depende", "dependência", "dependency", "requires", "necessário",
        "openai", "supabase", "database_url", "pgvector", "twilio", "whatsapp"
    ]
}

PRIORITY_HINTS = {
    "high": ["crítico", "critico", "obrigatório", "obrigatorio", "alta prioridade", "urgente", "bloqueia", "blocker"],
    "medium": ["importante", "recomendado", "deveria", "médio", "medio"],
    "low": ["opcional", "futuro", "pode", "talvez"]
}

def split_sentences(text: str):
    text = (text or "").replace("\r", "\n")
    chunks = re.split(r"(?<=[\.\!\?])\s+|\n+", text)
    return [c.strip() for c in chunks if len(c.strip()) >= 20]

def detect_priority(sentence: str) -> str:
    s = sentence.lower()
    for level, terms in PRIORITY_HINTS.items():
        if any(t in s for t in terms):
            return level.upper()
    return "MEDIUM"

def extract_items(source_id: str, text: str, metadata: dict | None = None) -> dict:
    sentences = split_sentences(text)

    items = []

    for sentence in sentences:
        low = sentence.lower()
        matched = []

        for category, terms in CATEGORIES.items():
            if any(t in low for t in terms):
                matched.append(category)

        if not matched:
            continue

        item = {
            "source_id": source_id,
            "type": matched[0],
            "all_types": matched,
            "priority": detect_priority(sentence),
            "text": sentence[:1200],
            "signals": matched,
            "metadata": metadata or {}
        }

        items.append(item)

    report = {
        "engine": "P4.79_KNOWLEDGE_EXTRACTION_ENGINE",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_id": source_id,
        "metadata": metadata or {},
        "total_items": len(items),
        "items": items,
        "summary": {}
    }

    for item in items:
        report["summary"][item["type"]] = report["summary"].get(item["type"], 0) + 1

    out = EXTRACTION_DIR / f"{source_id.replace('/', '_').replace(':', '_')}.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    return report
