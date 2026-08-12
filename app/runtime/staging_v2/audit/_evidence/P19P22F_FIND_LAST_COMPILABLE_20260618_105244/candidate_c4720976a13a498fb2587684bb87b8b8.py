from pathlib import Path

p = Path("app/api/whatsapp.py")
s = p.read_text(encoding="utf-8")

helper = '''
# P19P5_WHATSAPP_FINAL_GUARD_ONLY
def _p19p5_block_agricultural_automotive_contamination(inbound_text: str, answer: str, context: str = "") -> str:
    msg = f"{inbound_text or ''} {context or ''}".lower()
    out = str(answer or "")

    automotive = any(x in msg for x in [
        "mercedes", "classe a", "w168", "aks", "semi automatica", "semi automática",
        "atuador", "embreagem", "marcha", "câmbio", "cambio"
    ]) or ("desligado" in msg and "ligado" in msg and "marcha" in msg)

    contaminated = any(x in out.lower() for x in [
        "equipamento agrícola", "equipamento agricola", "trator", "tractor", "agrícola", "agricola"
    ])

    if automotive and contaminated:
        return (
            "Isso aponta para acionamento da embreagem/AKS do Mercedes Classe A. "
            "Se desligado entra marcha e ligado não entra, a embreagem provavelmente não está desacoplando totalmente. "
            "Prioridade: atuador AKS, curso da haste, garfo/rolamento, sangria/calibração e adaptação do sistema."
        )

    return out
# /P19P5_WHATSAPP_FINAL_GUARD_ONLY
'''

if "P19P5_WHATSAPP_FINAL_GUARD_ONLY" not in s:
    anchor = "# P19P.3_SAFE_RUNTIME_INTEGRATION"
    s = s.replace(anchor, helper + "\n" + anchor, 1)

old = "return out\n# /P19P.3_SAFE_RUNTIME_INTEGRATION"
new = "return _p19p5_block_agricultural_automotive_contamination(inbound_text, out, context)\n# /P19P.3_SAFE_RUNTIME_INTEGRATION"
s = s.replace(old, new, 1)

p.write_text(s, encoding="utf-8")
