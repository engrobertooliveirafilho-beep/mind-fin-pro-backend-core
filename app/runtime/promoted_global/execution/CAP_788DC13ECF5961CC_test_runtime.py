from app.api.whatsapp import eldora_primary_runtime_reply

sender = "restore_test_user"

inputs = [
    "como posso automatizar confinamento de boi?",
    "como eu faço?",
    "explique melhor",
    "e depois?"
]

for i in inputs:
    print("INPUT:", i)
    print("OUTPUT:", eldora_primary_runtime_reply(sender, i))
    print("-"*50)
