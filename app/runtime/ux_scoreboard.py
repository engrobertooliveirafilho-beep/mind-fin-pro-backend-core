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

LEAK_TERMS = [
    "mind/eldora","runtime estável v2","context fusion",
    "webhook produtivo","twilio validado"
]

FALLBACK_TERMS = [
    "não entendi","fallback","como posso ajudar hoje",
    "boa. isso ajuda bastante","qual camada",
    "memória contextual: aprofunde",
    "mantendo autoridade contextual",
    "o plano já está funcionando parcialmente"
]

def _norm(s:str)->str:
    return re.sub(r"\s+"," ",(s or "").strip().lower())

def score_message(message:str, reply:str)->UXScore:
    r = reply or ""
    rn = _norm(r)
    mn = _norm(message)
    flags=[]

    leak=int(any(x in rn for x in LEAK_TERMS))
    fallback=int(any(x in rn for x in FALLBACK_TERMS))

    words=re.findall(r"\b\w{4,}\b",rn)
    duplication=int(len(words)>5 and len(set(words))/max(1,len(words))<0.55)

    echo=int(len(mn)>3 and mn in rn)
    mojibake=int(any(x in r for x in ["├","ƒ","┬","┼","�"]))
    artificial=int(any(x in rn for x in [
        "mantendo autoridade contextual",
        "memória contextual:",
        "sem puxar outro domínio"
    ]))
    handback=int(any(x in rn for x in [
        "qual camada","você vai mexer","me conta"
    ]))

    size_ok=int(1<=len(r)<=220)
    context_ok=int(not leak and not fallback and len(rn)>3)

    if leak: flags.append("leak")
    if fallback: flags.append("fallback")
    if duplication: flags.append("duplication")
    if echo: flags.append("echo")
    if mojibake: flags.append("mojibake")
    if artificial: flags.append("artificial")
    if handback: flags.append("handback")
    if not size_ok: flags.append("size")
    if not context_ok: flags.append("context")

    score = (
        10.0
        - leak*3
        - fallback*2.5
        - duplication*1.5
        - echo*1.5
        - mojibake*2
        - artificial*2
        - handback*1.5
        - (1-size_ok)*1
        - (1-context_ok)*2
    )

    return UXScore(
        message=message,
        reply=reply,
        leak=leak,
        duplication=duplication,
        fallback=fallback,
        size_ok=size_ok,
        context_ok=context_ok,
        score=max(0.0,round(score,2)),
        flags=flags
    )

def score_batch(pairs:List[Dict[str,str]])->Dict:
    rows=[asdict(score_message(p["message"],p["reply"])) for p in pairs]
    avg=round(sum(r["score"] for r in rows)/max(1,len(rows)),2)
    return {
        "average_score":avg,
        "passed":avg>=8.5 and all(r["leak"]==0 for r in rows),
        "rows":rows
    }
