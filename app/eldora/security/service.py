import re

DANGEROUS_PATTERNS = ["ignore previous instructions", "reveal secrets", "admin token", "system prompt"]

def unicode_cleaner(text: str) -> str:
    return (text or "").encode("utf-8", "ignore").decode("utf-8").strip()

def prompt_firewall(text: str) -> dict:
    clean = unicode_cleaner(text).lower()
    blocked = any(p in clean for p in DANGEROUS_PATTERNS)
    return {"clean_text": clean, "blocked": blocked, "risk": "high" if blocked else "low"}

def abuse_score(text: str) -> dict:
    clean = unicode_cleaner(text)
    score = min(100, len(re.findall(r"[!]{3,}|http|token|senha|secret", clean.lower())) * 25)
    return {"score": score, "blocked": score >= 75}

def require_admin_token(token: str | None) -> bool:
    return bool(token and len(token) >= 12)

def block_public_admin_access(token: str | None) -> dict:
    ok = require_admin_token(token)
    return {"admin_allowed": ok, "public_admin_blocked": not ok}

def sanitize_routes_output(routes: list[str]) -> dict:
    safe = [r for r in routes if "/admin" not in r and "secret" not in r.lower()]
    return {"routes": safe, "sanitized": True}
