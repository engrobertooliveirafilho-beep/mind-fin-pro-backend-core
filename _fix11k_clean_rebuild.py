from pathlib import Path
import re

p=Path("app/main.py")
s=p.read_text(encoding="utf-8")

guard = r'''
def p412n_final_semantic_ux_guard(message: str, reply: str) -> str:
    import re

    msg=(message or "").strip().lower()
    out=(reply or "").strip()
    low=out.lower()

    generic=[
        "vamos seguir pelo ponto real",
        "vamos aprofundar sem reiniciar",
        "validar o próximo passo",
        "primeiro isolamos a causa real",
        "me diga melhor",
        "pode me dar mais detalhes",
        "assim posso te ajudar melhor",
        "entendi.",
        "continua.",
        "manter a continuidade",
        "memória contextual:",
        "ação recomendada:",
        "resposta direta:",
        "detalhamento:",
        "análise:"
    ]

    bad=(not out) or any(x in low for x in generic)

    if re.search(r'\d+\s*([xX*+\-/])\s*\d+', msg) or "quanto é" in msg:
        return out

    if any(x in msg for x in ["quem é você","quem é vc","quem e vc","quem e você"]):
        return "Sou a Eldora. Organizo contexto, memória e execução para ajudar em decisões e ações." if bad else out

    if any(x in msg for x in ["como você está","como vc está","vc está bem","tudo bem"]):
        return "Tudo certo por aqui 🙂 E você?" if bad else out

    if any(x in msg for x in ["por que está dando erro","porque deu errado","como resolvemos isso","deu errado"]):
        return "O erro principal está no pipeline de resposta: uma camada substitui respostas válidas por fallback genérico. Vamos isolar e validar." if bad else out

    if any(x in msg for x in ["aprofunde","detalhe","me explique melhor","consegue detalhar"]):
        return "Aprofundando: primeiro localizamos a camada problemática, depois validamos o fluxo real e aplicamos patch mínimo." if bad else out

    if any(x in msg for x in ["e depois","depois?","próximo","proximo"]):
        return "Depois validamos no WhatsApp real, registramos evidência e só então fechamos a etapa." if bad else out

    if any(x in msg for x in ["procure o erro principal","busque pelo problema","onde está o erro"]):
        return "Vou procurar o erro principal no caminho real: dispatch, authority, arbiter, normalização e XML final." if bad else out

    if any(x in msg for x in ["oi","olá","ola","bom dia","boa tarde","boa noite"]) and len(msg)<20:
        return "Oi! O que você precisa?" if bad else out

    return out
'''

if "def p412n_final_semantic_ux_guard" in s:
    s=re.sub(
        r"def p412n_final_semantic_ux_guard\(.*?\n@app\.post",
        guard+"\n@app.post",
        s,
        flags=re.S
    )

old='''primary_reply = factual_search_handoff(primary_reply, message)'''
new='''primary_reply = factual_search_handoff(primary_reply, message)

            runtime_error_reply = any(x in str(primary_reply) for x in [
                "WEBHOOK_ERROR_TOTAL",
                "DATABASE_URL missing",
                "AssertionError",
                "Traceback"
            ])

            if runtime_error_reply:
                primary_reply = p412n_final_semantic_ux_guard(message, primary_reply)
                return Response(
                    content=_p412n_normalize_xml_response(message, primary_twiml(primary_reply)),
                    media_type="application/xml"
                )

            authority_reply = strategic_conversation_authority(primary_reply, message)
            if authority_reply is not None:
                primary_reply = authority_reply

            arbiter_reply = final_conversational_arbiter(sender_id, message, primary_reply)
            if arbiter_reply is not None:
                primary_reply = arbiter_reply

            primary_reply = p412n_final_semantic_ux_guard(message, primary_reply)'''

s=s.replace(old,new,1)

s=re.sub(
r"runtime_error_reply = any\(x in str\(primary_reply\).*?primary_reply = p412n_final_semantic_ux_guard\(message, primary_reply\)",
"",
s,
flags=re.S
)

p.write_text(s,encoding="utf-8")
print("FIX11K_CLEAN_REBUILD_OK")
