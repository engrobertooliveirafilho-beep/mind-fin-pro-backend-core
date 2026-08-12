from app.api.whatsapp import eldora_primary_runtime_reply

cases = [
    ("audit_user","quero automatizar confinamento de boi"),
    ("audit_user","e depois?"),
    ("audit_user","prosseguir evolução do mind")
]

for sender,msg in cases:
    try:
        out = eldora_primary_runtime_reply(sender,msg)

        print("=" * 80)
        print("INPUT:")
        print(msg)

        print("")
        print("OUTPUT:")
        print(str(out)[:1000])

    except Exception as e:
        print("=" * 80)
        print("INPUT:")
        print(msg)

        print("")
        print("ERROR:")
        print(repr(e))
