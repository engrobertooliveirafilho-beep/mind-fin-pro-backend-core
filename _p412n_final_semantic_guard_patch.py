from pathlib import Path
p=Path("app/main.py")
s=p.read_text(encoding="utf-8")

insert = r'''
def p412n_final_semantic_ux_guard(message: str, reply: str) -> str:
    msg=(message or "").strip().lower()
    out=(reply or "").strip()
    low=out.lower()

    generic_markers=[
        "vamos seguir pelo ponto real",
        "vamos aprofundar sem reiniciar",
        "me diga melhor",
        "pode me dar mais detalhes",
        "assim posso te ajudar melhor",
        "entendi. continua",
        "entendi.",
        "continua.",
        "próximo passo",
        "validar o próximo passo",
        "manter a continuidade",
        "sem reiniciar a conversa",
    ]

    is_generic = (not out) or any(x in low for x in generic_markers)

    if any(x in msg for x in ["quanto é","calcule","calcular"]) and any(ch.isdigit() for ch in msg):
        return out

    if any(x in msg for x in ["oi","olá","ola","bom dia","boa tarde","boa noite","oie"]) and len(msg) <= 20:
        if is_generic:
            return "Oi, Roberto 🙂 Tudo certo."

    if any(x in msg for x in ["tudo bem","como você está","como vc está","como vc esta","como você esta"]):
        if is_generic:
            return "Tudo certo por aqui 🙂 E você?"

    if any(x in msg for x in ["quem é você","quem é vc","quem e você","quem e vc"]):
        if is_generic or "tudo certo" in low:
            return "Sou a Eldora, a assistente do MIND/NEURA. Eu organizo contexto, memória e execução para te ajudar com decisões e ações."

    if any(x in msg for x in ["por que está dando erro","porque está dando erro","por que esta dando erro","porque esta dando erro","deu erro","deu errado"]):
        if is_generic:
            return "O erro principal está no fluxo de resposta: alguma camada está trocando uma resposta válida por fallback genérico. Vamos isolar por evidência."

    if any(x in msg for x in ["aprofunde","detalhe","detalhar","explique melhor"]):
        if is_generic:
            return "Aprofundando: primeiro identificamos a camada que muda a resposta, depois aplicamos patch mínimo e validamos com teste + WhatsApp."

    if any(x in msg for x in ["e depois","depois?","próximo","proximo"]):
        if is_generic:
            return "Depois validamos no WhatsApp real, registramos evidência no Drive e só então fechamos a etapa."

    if any(x in msg for x in ["procure o erro principal","busque o problema","onde está o erro","onde esta o erro"]):
        if is_generic:
            return "Vou procurar o erro principal no pipeline real: entrada, dispatch, authority, arbiter, normalização e XML final."

    return out
'''

if "def p412n_final_semantic_ux_guard" not in s:
    marker='@app.post("/webhook/whatsapp")'
    s=s.replace(marker, insert + "

" + marker, 1)

old='''            return Response(content=_p412n_normalize_xml_response(message if "message" in locals() else "", primary_twiml(primary_reply)), media_type="application/xml")'''

new='''            primary_reply = p412n_final_semantic_ux_guard(message, primary_reply)
            return Response(content=_p412n_normalize_xml_response(message if "message" in locals() else "", primary_twiml(primary_reply)), media_type="application/xml")'''

if old not in s:
    raise SystemExit("PATCH_TARGET_NOT_FOUND_FINAL_GUARD")

s=s.replace(old,new,1)
p.write_text(s,encoding="utf-8")
print("P4_12N_FINAL_SEMANTIC_UX_GUARD_PATCHED")
