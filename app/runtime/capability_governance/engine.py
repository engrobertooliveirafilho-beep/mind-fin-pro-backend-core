import json
from dataclasses import asdict
from app.runtime.capability_governance.contract import GovernanceRequest
from app.runtime.capability_governance.selector import decide, infer_domain

def govern_text(text: str, context=None):
    request = GovernanceRequest(
        text=text,
        domain=infer_domain(text),
        context=context or {},
    )

    decision = decide(request)

    return {
        "request": asdict(request),
        "decision": {
            "selected": [asdict(x) for x in decision.selected],
            "rejected_count": len(decision.rejected),
            "reason": decision.reason,
            "mode": decision.mode,
            "final_authority": decision.final_authority,
        },
    }

if __name__ == "__main__":
    samples = [
        "como automatizar confinamento de boi?",
        "crie uma estratégia de marketing para a Eldora",
        "validar runtime trader FTMO em paper only",
        "minha Mercedes não entra ré",
        "corrigir resposta do WhatsApp",
        "prossiga",
    ]

    for s in samples:
        print(json.dumps(govern_text(s), indent=2, ensure_ascii=False))
