
from app.runtime.universal_conversation_authority import universal_conversation_reply

BAD_FACTUAL_BLEED = [
    "detalhe / risk", "detalhe / price", "comparação / compatibility",
    "compatibilidade:", "preço:", "risco:", "alternativas:",
    "kick starter", "cr250r", "ims", "red dragon"
]

PROGRESSIVE = ["detalhe melhor", "aprofunde", "ainda mais", "passo a passo", "explique melhor"]

def final_conversational_arbiter(sender_id: str, inbound: str, answer: str) -> str:
    msg = (inbound or "").lower()
    out = str(answer or "")
    low = out.lower()

    if any(x in msg for x in PROGRESSIVE) and any(x in low for x in BAD_FACTUAL_BLEED):
        synthetic = "passo a passo" if "passo a passo" in msg else "aprofunde"
        return out

    if out.count("\n\n") > 4 and any(x in msg for x in PROGRESSIVE):
        return out

    return out

