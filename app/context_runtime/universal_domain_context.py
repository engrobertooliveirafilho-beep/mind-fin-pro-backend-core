from __future__ import annotations
import json
import re
from pathlib import Path
from datetime import datetime, timezone

STORE = Path("_runtime_state/universal_domain_context_by_sender.json")

SHORT_FOLLOWUPS = {
    "quais", "quais?", "quais são", "quais sao",
    "prossiga", "continue", "continua", "e depois",
    "explique melhor", "detalhe", "sim", "ok"
}

DOMAIN_HINTS = {
    "fitness": ["emagrecer", "dieta", "treino", "musculação", "musculacao", "cardio", "hipertrofia"],
    "eldora_launch": ["lançar eldora", "lancar eldora", "lançamento", "lancamento", "marketing", "instagram", "tiktok"],
    "agro": ["boi", "gado", "confinamento", "pasto", "bezerro", "arroba", "fazenda"],
    "trader": ["trade", "trader", "ftmo", "backtest", "mt5", "metatrader", "mercado"],
    "auto": ["carro", "moto", "câmbio", "cambio", "embreagem", "motor", "mercedes"],
    "study": ["estudar", "prova", "faculdade", "concurso", "matemática", "matematica"]
}

def norm(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())

def is_short_followup(text: str) -> bool:
    return norm(text) in SHORT_FOLLOWUPS

def detect_domain(text: str) -> str:
    t = norm(text)
    for domain, hints in DOMAIN_HINTS.items():
        if any(h in t for h in hints):
            return domain
    if len(t.split()) >= 2:
        return "general"
    return ""

def extract_subject(text: str) -> str:
    t = norm(text)
    return t[:160]

def _load():
    if STORE.exists():
        try:
            return json.loads(STORE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def _save(data):
    STORE.parent.mkdir(parents=True, exist_ok=True)
    STORE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def bind(sender: str, text: str, domain: str | None = None):
    sid = sender or "unknown"
    d = domain or detect_domain(text)
    if not d:
        return get(sid)

    data = _load()
    data[sid] = {
        "active_domain": d,
        "active_subject": extract_subject(text),
        "last_user_text": text or "",
        "followup_policy": "continue_same_domain",
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    _save(data)
    return data[sid]

def get(sender: str):
    return _load().get(sender or "unknown", {})

def resolve(sender: str, text: str):
    t = norm(text)
    ctx = get(sender)

    if is_short_followup(t):
        return {
            "mode": "followup",
            "has_context": bool(ctx.get("active_domain")),
            "context": ctx
        }

    d = detect_domain(t)
    if d:
        ctx = bind(sender, text, d)
        return {
            "mode": "new_domain",
            "has_context": True,
            "context": ctx
        }

    return {
        "mode": "none",
        "has_context": False,
        "context": ctx
    }
