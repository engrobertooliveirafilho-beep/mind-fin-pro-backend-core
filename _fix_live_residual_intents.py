from pathlib import Path

p=Path("app/main.py")
s=p.read_text(encoding="utf-8")

anchor='''            if any(x in msg for x in ["me explique melhor","explique melhor"]):
                primary_reply="Vou explicar melhor mantendo o contexto atual e aprofundando o ponto anterior sem mudar de direção."'''

patch='''            if any(x in msg for x in ["como vc esta","como vc está","como você está","como voce esta","vc esta bem","vc está bem"]):
                primary_reply="Tudo certo por aqui. E você?"

            elif any(x in msg for x in ["conseguiu entender","todas as implantações","todas as implantacoes"]):
                primary_reply="Sim. Entendi as implantações principais: local corrigido, Render sincronizado e agora falta ajustar os intents residuais do live."

            elif any(x in msg for x in ["ainda esta errado","ainda está errado","continua errado","esta errado","está errado"]):
                primary_reply="Entendi. O erro ainda está no roteamento de intenção do live; vamos corrigir o branch que caiu no fallback."

            elif any(x in msg for x in ["me explique melhor","explique melhor"]):
                primary_reply="Vou explicar melhor mantendo o contexto atual e aprofundando o ponto anterior sem mudar de direção."'''

if anchor not in s:
    raise SystemExit("ANCHOR_NOT_FOUND")

s=s.replace(anchor,patch,1)

# remover emojis das respostas hardcoded principais para evitar ???? no TwiML
s=s.replace("Oi, Roberto 👋 Tudo certo?","Oi, Roberto. Tudo certo?")
s=s.replace("Sou a Eldora 🙂 O que você quer saber?","Sou a Eldora. O que você quer saber?")
s=s.replace("Tudo certo por aqui 🙂 E você?","Tudo certo por aqui. E você?")
s=s.replace("Tudo certo por aqui 🙂","Tudo certo por aqui.")

p.write_text(s,encoding="utf-8")
print("LIVE_RESIDUAL_INTENTS_PATCH_OK")
