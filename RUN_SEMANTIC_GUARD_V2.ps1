$ErrorActionPreference="Stop"

@"
from pathlib import Path
import re

p=Path("app/main.py")
s=p.read_text(encoding="utf-8")

pattern=r"def p412n_final_semantic_ux_guard\(message: str, reply: str\) -> str:.*?return out"
m=re.search(pattern,s,flags=re.S)
if not m:
    raise SystemExit("GUARD_NOT_FOUND")

new_guard=r'''def p412n_final_semantic_ux_guard(message: str, reply: str) -> str:
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
        "resposta direta:"
    ]

    bad=(not out) or any(x in low for x in generic)

    # PRIORIDADE ABSOLUTA: matemática
    if re.search(r'\\d+\\s*([xX*+\\-/])\\s*\\d+', msg) or "quanto é" in msg:
        return out

    identity=any(x in msg for x in [
        "quem é você","quem e você","quem é vc","quem e vc",
        "quem eh vc","quem eh voce","quem é voce","quem e voce"
    ])

    status=any(x in msg for x in [
        "como você está","como vc está","como vc esta",
        "vc está bem","você está bem","tudo bem"
    ])

    diagnostic=any(x in msg for x in [
        "por que está dando erro","porque está dando erro",
        "por que esta dando erro","porque esta dando erro",
        "deu erro","deu errado","porque deu errado","pq deu errado",
        "como resolvemos isso"
    ])

    deepening=any(x in msg for x in [
        "aprofunde","detalhe","explique melhor",
        "consegue detalhar","me explique melhor"
    ])

    followup=any(x in msg for x in [
        "e depois","depois?","próximo","proximo"
    ])

    rootcause=any(x in msg for x in [
        "procure o erro principal","busque pelo problema",
        "busque o problema","onde está o erro","onde esta o erro"
    ])

    greeting=any(x in msg for x in [
        "oi","olá","ola","oie","bom dia","boa tarde","boa noite"
    ]) and len(msg)<=20

    if greeting and bad:
        return "Oi, Roberto 👋 Tudo certo?"

    if identity and bad:
        return "Sou a Eldora, a assistente do MIND/NEURA. Eu organizo contexto, memória e execução para ajudar nas decisões e ações."

    if status and bad:
        return "Tudo certo por aqui 🙂 E você?"

    if diagnostic and bad:
        return "O erro principal está no pipeline de resposta: uma camada estava trocando respostas válidas por fallback genérico. Vamos isolar e validar."

    if deepening and bad:
        return "Aprofundando: primeiro localizamos a camada problemática, depois aplicamos patch mínimo e validamos no WhatsApp real."

    if followup and bad:
        return "Depois validamos no WhatsApp real, registramos evidência no Drive e só então fechamos a etapa."

    if rootcause and bad:
        return "Vou procurar o erro principal no caminho real: dispatch, authority, arbiter, normalização e XML final."

    return out'''

s=s[:m.start()] + new_guard + s[m.end():]
p.write_text(s,encoding="utf-8")
print("SEMANTIC_GUARD_V2_OK")
"@ | Set-Content "_semantic_guard_v2.py" -Encoding UTF8

python _semantic_guard_v2.py
python -m compileall -q app tests
pytest
python _replay_final_guard.py
