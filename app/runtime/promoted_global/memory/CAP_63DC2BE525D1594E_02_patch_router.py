from pathlib import Path

p = Path("app/domains/universal_domain_router.py")
s = p.read_text(encoding="utf-8")

old = '''    return generic_contextual_reply(text, ctx)
'''

new = '''    if domain == "subject":
        subject = ctx.get("active_subject", "esse assunto")
        tokens = ctx.get("subject_tokens", [])
        core = ", ".join(tokens[:6]) if tokens else subject
        return (
            f"Continuando no mesmo assunto: {subject}. "
            f"Pontos centrais: {core}. "
            f"Agora eu aprofundo em passos práticos, riscos, dados necessários e próxima ação."
        )

    return generic_contextual_reply(text, ctx)
'''

if "Pontos centrais:" not in s:
    s = s.replace(old, new, 1)

p.write_text(s, encoding="utf-8")
print("P19P30B_ROUTER_PATCH_OK")
