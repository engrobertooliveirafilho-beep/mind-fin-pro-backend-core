from app.api.whatsapp import eldora_primary_runtime_reply

sender = "p19p16_local_case"
cases = [
    "como posso automatizar meu confinamento de boi, para não precisar de funcionario?",
    "como eu faço?",
    "explique melhor",
    "quero detalhes sobre confinamento de boi",
]

for msg in cases:
    print("\nUSER:", msg)
    out = eldora_primary_runtime_reply(sender, msg)
    print("MIND:", out)
    print("CHECK_BAD_GENERIC:", any(x in out.lower() for x in [
        "organizar ideias",
        "não tenho informação suficiente",
        "consultar uma fonte real",
        "sistema de alimentação automatizado: invista"
    ]))
