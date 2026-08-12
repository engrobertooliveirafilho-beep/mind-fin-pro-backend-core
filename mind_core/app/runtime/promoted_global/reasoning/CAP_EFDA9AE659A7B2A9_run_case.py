from app.api.whatsapp import eldora_primary_runtime_reply

cases = [
    "como posso automatizar meu confinamento de boi, para não precisar de funcionario?",
    "como eu faço?",
    "explique melhor",
    "quero detalhes",
]

sender = "p19p15_local_case"
for msg in cases:
    print("\nUSER:", msg)
    out = eldora_primary_runtime_reply(sender, msg)
    print("MIND:", out)
    print("CHECK_GENERIC:", any(x in out.lower() for x in [
        "invista em alimentadores automáticos",
        "considere as seguintes etapas",
        "considere os seguintes passos",
        "sistema de alimentação automatizado"
    ]))
