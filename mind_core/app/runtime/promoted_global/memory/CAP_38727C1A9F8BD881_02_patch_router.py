from pathlib import Path

p = Path("app/domains/universal_domain_router.py")
s = p.read_text(encoding="utf-8")

if "P19P30_DISCOVERED_DOMAIN_REPLY" not in s:
    s = s.replace(
'''    return generic_contextual_reply(text, ctx)
''',
'''    if domain == "discovered":
        subject = ctx.get("active_subject", "esse assunto")
        tokens = ctx.get("subject_tokens", [])
        core = ", ".join(tokens[:5]) if tokens else subject
        return (
            f"Continuando no mesmo assunto: {subject}. "
            f"Os pontos centrais são: {core}. "
            f"Agora eu aprofundo em passos práticos, riscos, próximos dados necessários e execução."
        )

    return generic_contextual_reply(text, ctx)
# P19P30_DISCOVERED_DOMAIN_REPLY
''',
    1)

p.write_text(s, encoding="utf-8")
print("P19P30_ROUTER_DISCOVERED_PATCH_OK")
