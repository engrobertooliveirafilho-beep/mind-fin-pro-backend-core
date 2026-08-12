from pathlib import Path

p = Path("app/api/whatsapp.py")
s = p.read_text(encoding="utf-8")

helper = '''
# P19P7_CONTEXT_MEMORY_FOLLOWUP_EXPANSION
def _p19p7_contextual_followup_expansion(inbound_text: str, answer: str, context: str = "") -> str:
    msg = (inbound_text or "").lower()
    ctx = (context or "").lower()
    out = str(answer or "")

    is_followup = any(x in msg for x in [
        "quais são elas",
        "quais sao elas",
        "explique melhor",
        "explica melhor",
        "aprofundar",
        "aprofunde",
        "mais detalhes",
        "continue",
        "continua"
    ])

    confinement_context = any(x in (msg + " " + ctx + " " + out.lower()) for x in [
        "confinamento",
        "boi",
        "gado",
        "trato",
        "cocho",
        "silo",
        "ração",
        "racao",
        "alimentação",
        "alimentacao"
    ])

    generic_restart = any(x in out.lower() for x in [
        "considere os seguintes passos",
        "considere as seguintes etapas",
        "automatizar sua operação",
        "automatizar a operação",
        "instale sensores",
        "sensores e monitoramento",
        "monitoramento de ambiente"
    ])

    if is_followup and confinement_context and generic_restart:
        if "quais são elas" in msg or "quais sao elas" in msg:
            return (
                "As principais tecnologias para automatizar um confinamento são: "
                "1) trato automatizado, 2) silo com controle de nível, 3) vagão misturador com balança, "
                "4) leitura de cocho por câmera, 5) bebedouro monitorado, 6) balança eletrônica de passagem, "
                "7) câmeras com alerta, 8) software de gestão zootécnica e financeira. "
                "Na prática, o primeiro ponto para atacar é o trato, porque é onde mais se gasta tempo todo dia."
            )

        return (
            "Explicando melhor: a automação do confinamento precisa começar pelo trato. "
            "O fluxo ideal é ter silo, balança, misturador e distribuição integrados. "
            "O sistema pesa os ingredientes da dieta, mistura na proporção correta e controla quanto foi entregue em cada lote. "
            "Depois você adiciona leitura de cocho por câmera, controle de água e balança eletrônica para acompanhar ganho de peso. "
            "Com isso, o funcionário deixa de fazer tarefa repetitiva e passa a supervisionar exceções: falta de ração, queda de consumo, problema em bebedouro ou animal fora do padrão."
        )

    return out
# /P19P7_CONTEXT_MEMORY_FOLLOWUP_EXPANSION
'''

if "P19P7_CONTEXT_MEMORY_FOLLOWUP_EXPANSION" not in s:
    anchor = "# P19P6_WHATSAPP_FOLLOWUP_EXPANSION"
    s = s.replace(anchor, helper + "\n" + anchor, 1)

old = "return _p19p6_expand_bad_followup_template(inbound_text, _p19p5_block_agricultural_automotive_contamination(inbound_text, out, context), context)"
new = "return _p19p7_contextual_followup_expansion(inbound_text, _p19p6_expand_bad_followup_template(inbound_text, _p19p5_block_agricultural_automotive_contamination(inbound_text, out, context), context), context)"
s = s.replace(old, new, 1)

p.write_text(s, encoding="utf-8")
