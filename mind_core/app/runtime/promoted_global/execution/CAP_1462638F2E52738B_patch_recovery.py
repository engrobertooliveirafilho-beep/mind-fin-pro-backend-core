from pathlib import Path

p = Path("app/humanization/universal_recovery_runtime.py")
s = p.read_text(encoding="utf-8")

s = s.replace(
    'return "Não tenho informação suficiente para afirmar com segurança. Vou precisar consultar uma fonte real antes de responder."',
    'return "Preciso confirmar isso com uma fonte real antes de afirmar."'
)

if "P19P28G_RECOVERY_CONTAINMENT" not in s:
    s += '''

# P19P28G_RECOVERY_CONTAINMENT
def p19p28g_should_use_factual_recovery(user_message: str) -> bool:
    t = (user_message or "").strip().lower()
    if t in ["quais", "quais?", "prossiga", "continue", "continua", "e depois", "explique melhor", "ok", "sim", "não", "nao"]:
        return False
    return any(x in t for x in ["fonte", "notícia", "noticia", "preço", "preco", "cotação", "cotacao", "lei", "oficial", "hoje", "agora"])
'''
p.write_text(s, encoding="utf-8")
print("RECOVERY_PATCH_OK")
