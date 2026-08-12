from pathlib import Path

p = Path("app/api/whatsapp.py")
s = p.read_text(encoding="utf-8")

helper = '''
# P19P8_GENERIC_RESTART_SUPPRESSION
def _p19p8_suppress_generic_restart(inbound_text: str, answer: str, context: str = "") -> str:
    msg = (inbound_text or "").lower()
    ctx = (context or "").lower()
    out = str(answer or "")
    low = out.lower()

    followup = any(x in msg for x in [
        "explique melhor",
        "explica melhor",
        "como eu faço",
        "como faço",
        "aprofunde",
        "mais detalhes",
        "quais são elas",
        "quais sao elas"
    ])

    confinement = any(x in (msg + " " + ctx + " " + low) for x in [
        "confinamento",
        "boi",
        "bois",
        "gado",
        "trato",
        "cocho",
        "alimentação",
        "alimentacao",
        "ração",
        "racao"
    ])

    generic_restart = any(x in low for x in [
        "para automatizar seu confinamento",
        "para automatizar o confinamento",
        "automatizar o confinamento de bois",
        "considere os seguintes passos",
        "considere as seguintes etapas",
        "sistema de alimentação automatizado",
        "invista em alimentadores automáticos",
        "instale sensores"
    ])

    if followup and confinement and generic_restart:
        return (
            "Indo mais fundo: o centro da automação no confinamento é o trato. "
            "Você precisa montar um fluxo em que a dieta sai do silo, passa por pesagem, mistura e distribuição com o mínimo de intervenção humana. "
            "Na prática existem três níveis. Primeiro: alimentador ou vagão programado para entregar ração por lote. "
            "Segundo: balança integrada no misturador para pesar milho, núcleo, volumoso e suplemento com precisão. "
            "Terceiro: leitura de cocho por câmera ou aplicativo para ajustar a quantidade do próximo trato. "
            "Depois disso entram bebedouros monitorados, câmeras nos currais, balança de passagem e alertas no celular. "
            "Se você quer reduzir funcionário, comece automatizando alimentação e leitura de cocho, porque são as tarefas que mais consomem rotina diária."
        )

    return out
# /P19P8_GENERIC_RESTART_SUPPRESSION
'''

if "P19P8_GENERIC_RESTART_SUPPRESSION" not in s:
    anchor = "# P19P7_CONTEXT_MEMORY_FOLLOWUP_EXPANSION"
    s = s.replace(anchor, helper + "\n" + anchor, 1)

old = "return _p19p7_contextual_followup_expansion(inbound_text, _p19p6_expand_bad_followup_template(inbound_text, _p19p5_block_agricultural_automotive_contamination(inbound_text, out, context), context), context)"
new = "return _p19p8_suppress_generic_restart(inbound_text, _p19p7_contextual_followup_expansion(inbound_text, _p19p6_expand_bad_followup_template(inbound_text, _p19p5_block_agricultural_automotive_contamination(inbound_text, out, context), context), context), context)"
s = s.replace(old, new, 1)

p.write_text(s, encoding="utf-8")
