
import re

PREFIXES = [
    r"^quero\s+comprar\s+",
    r"^quero\s+montar\s+",
    r"^quero\s+criar\s+",
    r"^quero\s+fazer\s+",
    r"^preciso\s+de\s+",
    r"^preciso\s+",
]

def subject_alias(subject:str)->str:
    s=str(subject or "").strip()

    for pat in PREFIXES:
        s=re.sub(pat,"",s,flags=re.I)

    s=re.sub(r"^(um|uma|o|a)\s+","",s,flags=re.I)
    s=re.sub(r"\s+"," ",s).strip()

    return s or str(subject or "").strip()
