from app.runtime.p4_13g_router import route_natural_whatsapp

cases = [
    "quero emagrecer",
    "monte um plano pra mim",
    "quais",
    "crie um",
    "prossiga",
    "quero deixar vc mais humanizada"
]

for c in cases:
    print("CASE:", c)
    print("ROUTE:", route_natural_whatsapp(c))
    print("---")
