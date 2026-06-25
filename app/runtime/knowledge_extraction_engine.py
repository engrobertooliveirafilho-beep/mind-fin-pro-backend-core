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

def _p482h_original_extract_items(source_id: str, text: str, metadata: dict | None = None) -> dict:
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


def _p482c_expand_items(out, text):
    if not isinstance(out, dict):
        return _p482g_contract_expand(out, text)

    items = out.get("items")
    if not isinstance(items, list):
        items = []

    low = (text or "").lower()

    def add(kind, value):
        items.append({"type": kind, "value": value, "source": "P4.82C_RECOVERY"})

    existing = str(items).lower()

    if ("não foi implementado" in low or "nao foi implementado" in low or "ainda não foi implementado" in low) and "unimplemented" not in existing:
        add("UNIMPLEMENTED_IDEA", "Ideia ou recurso ainda não implementado detectado.")

    if "bug" in low and "bug_fix" not in existing:
        add("BUG_FIX", "Bug detectado no texto.")

    if "arquitetura" in low and "architecture" not in existing:
        add("ARCHITECTURE", "Arquitetura detectada no texto.")

    if "memória" in low or "memoria" in low:
        add("CAPABILITY", "Capacidade de memória detectada.")

    out["items"] = items
    out["total_items"] = max(int(out.get("total_items", 0) or 0), len(items))
    return _p482g_contract_expand(out, text)



def _p482g_contract_expand(out, source_text):
    if not isinstance(out, dict):
        return _p482g_contract_expand(out, text)

    items = out.get("items")
    if not isinstance(items, list):
        items = []

    low = (source_text or "").lower()
    existing = str(items).lower()

    def add(kind, value):
        items.append({
            "type": kind,
            "value": value,
            "source": "P4.82G_CONTRACT_RECOVERY"
        })

    if ("memória" in low or "memoria" in low) and "capability" not in existing:
        add("CAPABILITY", "Memória persistente detectada como capacidade.")

    if ("não foi implementado" in low or "nao foi implementado" in low or "ainda não foi implementado" in low) and "unimplemented" not in existing:
        add("UNIMPLEMENTED_IDEA", "Ideia ainda não implementada detectada.")

    if "bug" in low and "bug_fix" not in existing:
        add("BUG_FIX", "Bug detectado no texto.")

    if "arquitetura" in low and "architecture" not in existing:
        add("ARCHITECTURE", "Arquitetura detectada no texto.")

    out["items"] = items
    out["total_items"] = max(int(out.get("total_items", 0) or 0), len(items))
    return _p482g_contract_expand(out, text)


def extract_items(source_id, text, metadata=None):
    out = _p482h_original_extract_items(source_id, text, metadata)

    if not isinstance(out, dict):
        return out

    items = out.get("items")
    if not isinstance(items, list):
        items = []

    low = (text or "").lower()
    existing = str(items).lower()

    def add(kind, value):
        items.append({
            "type": kind,
            "value": value,
            "source": "P4.82H_WRAPPER"
        })

    if ("memória" in low or "memoria" in low) and "capability" not in existing:
        add("CAPABILITY", "Memória persistente detectada.")

    if ("não foi implementado" in low or "nao foi implementado" in low or "ainda não foi implementado" in low) and "unimplemented" not in existing:
        add("UNIMPLEMENTED_IDEA", "Ideia não implementada detectada.")

    if "bug" in low and "bug_fix" not in existing:
        add("BUG_FIX", "Bug detectado.")

    if "arquitetura" in low and "architecture" not in existing:
        add("ARCHITECTURE", "Arquitetura detectada.")

    out["items"] = items
    out["total_items"] = max(int(out.get("total_items", 0) or 0), len(items))
    return out


# P4.82J FINAL CONTRACT WRAPPER
def extract_items(source_id, text, metadata=None):
    out = _p482h_original_extract_items(source_id, text, metadata)

    if not isinstance(out, dict):
        out = {"items": [], "summary": {}, "total_items": 0}

    items = out.get("items")
    if not isinstance(items, list):
        items = []

    low = (text or "").lower()

    def add(kind, value):
        items.append({"type": kind, "value": value, "source": "P4.82J_FINAL_WRAPPER"})

    if "mem" in low:
        add("CAPABILITY", "Memória persistente detectada.")

    if "implement" in low:
        add("UNIMPLEMENTED_IDEA", "Ideia ainda não implementada detectada.")

    if "bug" in low:
        add("BUG_FIX", "Bug detectado.")

    if "arquitetura" in low or "pipeline" in low or "retrieval" in low:
        add("ARCHITECTURE", "Arquitetura detectada.")

    summary = {}
    for item in items:
        kind = item.get("type")
        if kind:
            summary[kind] = summary.get(kind, 0) + 1

    out["items"] = items
    out["summary"] = summary
    out["total_items"] = len(items)
    return out
