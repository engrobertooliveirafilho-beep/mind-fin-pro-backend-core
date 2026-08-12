from app.api.whatsapp import eldora_primary_runtime_reply

tests = [
    "como posso automatizar confinamento de boi?",
    "como eu faço?",
    "explique melhor",
    "e depois?",
    "vc esta mto superficial"
]

sender = "test_user"

for t in tests:
    try:
        r = eldora_primary_runtime_reply(sender, t)
        print("INPUT:", t)
        print("OUTPUT:", r)
        print("-"*40)
    except Exception as e:
        print("ERROR:", e)
