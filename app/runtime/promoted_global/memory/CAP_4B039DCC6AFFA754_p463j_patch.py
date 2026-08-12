from pathlib import Path

p = Path("app/api/whatsapp.py")
s = p.read_text(encoding="utf-8")

old = '''    progressive_followup = any(x in t for x in [
        "aprofunde","aprofundar","continue_context","prossiga","e depois",
        "detalhe melhor","explique melhor","ainda mais","passo a passo"
    ])
'''

new = '''    progressive_followup = any(x in t for x in [
        "aprofunde","aprofundar","continue_context","prossiga","e depois",
        "detalhe melhor","explique melhor","ainda mais","passo a passo",
        "qual próximo passo","qual proximo passo","próximo passo","proximo passo",
        "qual o próximo","qual o proximo","e agora","como sigo","como continuar",
        "continua","continue","seguir","avançar","avancar"
    ])
'''

if old not in s:
    raise SystemExit("PATCH_TARGET_NOT_FOUND_PROGRESSIVE_FOLLOWUP")

s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")
print("PATCH_APPLIED_OK")
