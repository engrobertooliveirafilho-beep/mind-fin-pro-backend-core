from app.context_runtime.universal_domain_context import resolve
from app.domains.universal_domain_router import route_domain_reply

sender = "+DIRECT"

cases = [
    "quero validar estratégia FTMO",
    "continue",
    "quero abrir uma franquia de sorvete",
    "prossiga",
    "como montar uma escola de inglês",
    "quais",
]

for msg in cases:
    resolved = resolve(sender, msg)
    print("INPUT:", msg)
    print("RESOLVED:", resolved)
    ctx = resolved.get("context") or {}
    if ctx:
        print("ROUTED:", route_domain_reply(msg, ctx))
    print("-" * 80)
