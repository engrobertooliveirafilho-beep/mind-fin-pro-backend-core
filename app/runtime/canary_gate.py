import json, os, time
from pathlib import Path

LEDGER = Path("_evidence/CANARY_RUNTIME_LEDGER.jsonl")

def canary_allowed(sender_id: str) -> bool:
    raw = os.getenv("CANARY_ALLOWED_SENDERS", "").strip()
    if not raw:
        return True
    allowed = [x.strip() for x in raw.split(",") if x.strip()]
    return str(sender_id or "").strip() in allowed

def semantic_enabled() -> bool:
    return os.getenv("SEMANTIC_RUNTIME_ENABLED", "true").lower() not in ("0","false","off","no")

def score_reply(message: str, reply: str) -> dict:
    r = str(reply or "")
    low = r.lower()
    return {
        "chars": len(r),
        "fallback": int("não entendi" in low or "reformule" in low),
        "english": int("equals" in low or "here are" in low),
        "too_long": int(len(r) > 650),
        "empty": int(not r.strip()),
        "score": max(0, 10 - 3*int("não entendi" in low or "reformule" in low) - 2*int(len(r)>650) - 2*int("equals" in low) - 5*int(not r.strip()))
    }

def log_canary(sender_id: str, message: str, reply: str, provider: str = "", extra: dict | None = None):
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "ts": int(time.time()),
        "sender_id": sender_id,
        "message": str(message or "")[:300],
        "reply": str(reply or "")[:900],
        "provider": provider,
        "score": score_reply(message, reply),
        "extra": extra or {},
    }
    with LEDGER.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row

def canary_health():
    rows = []
    if LEDGER.exists():
        rows = [json.loads(x) for x in LEDGER.read_text(encoding="utf-8", errors="ignore").splitlines()[-200:] if x.strip()]
    total = len(rows)
    avg = round(sum(r["score"]["score"] for r in rows)/total, 2) if total else None
    fallback = sum(r["score"]["fallback"] for r in rows)
    return {
        "status": "CANARY_HEALTH",
        "semantic_enabled": semantic_enabled(),
        "allowlist_configured": bool(os.getenv("CANARY_ALLOWED_SENDERS", "").strip()),
        "total_recent": total,
        "avg_score": avg,
        "fallback_count": fallback,
        "fallback_rate": round(fallback/total, 4) if total else 0,
        "ready_for_p414": bool(total >= 10 and avg and avg >= 8.5 and fallback/total < 0.03),
    }
