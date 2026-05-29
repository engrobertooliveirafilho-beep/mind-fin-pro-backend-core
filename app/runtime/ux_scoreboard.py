from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import Dict, List
import re

@dataclass
class UXScore:
    message: str
    reply: str
    leak: int
    duplication: int
    fallback: int
    size_ok: int
    context_ok: int
    score: float
    flags: List[str]

LEAK_TERMS = ["MIND/Eldora", "Runtime estável V2", "Context Fusion", "webhook produtivo", "Twilio validado"]
FALLBACK_TERMS = ["não entendi", "não recebi conteúdo", "fallback", "frase genérica", "como posso ajudar hoje"]

def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())

def score_message(message: str, reply: str) -> UXScore:
    r = reply or ""
    rn = _norm(r)
    flags = []
    leak = int(any(t.lower() in rn for t in LEAK_TERMS))
    fallback = int(any(t in rn for t in FALLBACK_TERMS))
    duplication = int(len(set(re.findall(r"\b\w{4,}\b", rn))) < max(1, len(re.findall(r"\b\w{4,}\b", rn)) * 0.55) and len(rn) > 80)
    size_ok = int(1 <= len(r) <= 220)
    context_ok = int(not fallback and not leak and len(rn) > 3)
    if leak: flags.append("leak")
    if fallback: flags.append("fallback")
    if duplication: flags.append("duplication")
    if not size_ok: flags.append("size")
    if not context_ok: flags.append("context")
    score = 10.0 - leak*3 - fallback*2.5 - duplication*1.5 - (1-size_ok)*1 - (1-context_ok)*2
    return UXScore(message, reply, leak, duplication, fallback, size_ok, context_ok, max(0.0, round(score, 2)), flags)

def score_batch(pairs: List[Dict[str, str]]) -> Dict:
    rows = [asdict(score_message(p["message"], p["reply"])) for p in pairs]
    avg = round(sum(r["score"] for r in rows) / max(1, len(rows)), 2)
    return {"average_score": avg, "passed": avg >= 8.5 and all(r["leak"] == 0 and r["fallback"] == 0 for r in rows), "rows": rows}
