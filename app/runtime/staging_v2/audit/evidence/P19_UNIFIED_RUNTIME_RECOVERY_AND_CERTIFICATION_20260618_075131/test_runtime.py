import sys
import os

sys.path.append(os.getcwd())

from app.api.whatsapp import eldora_primary_runtime_reply

sender = "unified_test"

tests = [
    "como posso automatizar confinamento de boi?",
    "como eu faço?",
    "explique melhor",
    "e depois?",
    "vc esta mto superficial"
]

for t in tests:
    print("INPUT:", t)
    print("OUTPUT:", eldora_primary_runtime_reply(sender, t))
    print("-"*60)
