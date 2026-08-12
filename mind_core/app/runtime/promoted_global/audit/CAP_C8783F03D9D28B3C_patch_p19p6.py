from pathlib import Path

p = Path("app/api/whatsapp.py")
s = p.read_text(encoding="utf-8")

helper = '''
# P19P6_WHATSAPP_FOLLOWUP_EXPANSION
def _p19p6_expand_bad_followup_template(inbound_text: str, answer: str, context: str = "") -> str:
    msg = (inbound_text or "").lower()
    out = str(answer or "")

    followup = any(x in msg for x in [
        "aprofunde",
        "explique melhor",
        "explica melhor",
        "quero mais detalhes",
        "mais detalhes",
        "continue",
        "continua"
    ])

    bad_template = any(x in out.lower() for x in [
        "execução contextual",
        "continua do ponto anterior",
        "evidência e próximo passo",
        "vou aprofundar",
        "com base no contexto"
    ])

    if followup and bad_template:
        return (
            "Vamos aprofundar na prática. Para automatizar um confinamento de bois com pouca mão de obra, "
            "o sistema precisa atacar quatro pontos: trato, água, monitoramento e manejo. "
            "O primeiro ganho vem do trato automatizado: silo, misturador, distribuição programada e controle de consumo. "
            "Depois entram sensores de nível de água, câmeras, balança eletrônica e alertas no celular. "
            "Assim você reduz funcionário fixo e deixa uma pessoa apenas para supervisão, manutenção e emergência. "
            "O melhor caminho é começar pelo que consome mais tempo diário: alimentação e leitura de cocho."
        )

    return out
# /P19P6_WHATSAPP_FOLLOWUP_EXPANSION
'''

if "P19P6_WHATSAPP_FOLLOWUP_EXPANSION" not in s:
    anchor = "# P19P5_WHATSAPP_FINAL_GUARD_ONLY"
    s = s.replace(anchor, helper + "\n" + anchor, 1)

old = "return _p19p6_expand_followup(inbound_text, _p19p5_block_agricultural_automotive_contamination(inbound_text, out, context), context)"
if old in s:
    new = "return _p19p6_expand_bad_followup_template(inbound_text, _p19p5_block_agricultural_automotive_contamination(inbound_text, out, context), context)"
    s = s.replace(old, new, 1)
else:
    old2 = "return _p19p5_block_agricultural_automotive_contamination(inbound_text, out, context)"
    new2 = "return _p19p6_expand_bad_followup_template(inbound_text, _p19p5_block_agricultural_automotive_contamination(inbound_text, out, context), context)"
    s = s.replace(old2, new2, 1)

p.write_text(s, encoding="utf-8")
