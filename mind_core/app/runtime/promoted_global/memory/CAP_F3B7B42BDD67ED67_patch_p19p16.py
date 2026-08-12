from pathlib import Path

p = Path("app/api/whatsapp.py")
s = p.read_text(encoding="utf-8")

helper = '''
# P19P16_CONFINEMENT_DOMAIN_INTERCEPTOR
def _p19p16_confinement_domain_interceptor(inbound_text: str, context: str = "") -> str | None:
    msg = f"{inbound_text or ''} {context or ''}".lower()

    has_domain = any(x in msg for x in [
        "confinamento", "boi", "bois", "gado", "cocho", "trato", "ração", "racao"
    ])

    has_need = any(x in msg for x in [
        "automatizar", "automação", "automacao", "funcionario", "funcionário",
        "como eu faço", "como faco", "como faço", "explique melhor",
        "quero detalhes", "mais detalhes", "aprofunde"
    ])

    if not (has_domain and has_need):
        return None

    return (
        "Para automatizar um confinamento de boi sem depender tanto de funcionário, comece pelo trato. "
        "O fluxo ideal é: silo com controle de nível, balança para pesar ingredientes, misturador/vagão, "
        "distribuição por lote e leitura de cocho. Depois entram bebedouros monitorados, câmeras nos currais, "
        "balança de passagem e alertas no celular. Na prática: primeiro automatize alimentação e leitura de cocho; "
        "depois água, pesagem e monitoramento. Isso reduz tarefa repetitiva e deixa a pessoa só para supervisão, "
        "manutenção e emergência."
    )
# /P19P16_CONFINEMENT_DOMAIN_INTERCEPTOR
'''

if "P19P16_CONFINEMENT_DOMAIN_INTERCEPTOR" not in s:
    s = s.replace("# P19P9_UNIVERSAL_WHATSAPP_OUTPUT_GUARD", helper + "\n# P19P9_UNIVERSAL_WHATSAPP_OUTPUT_GUARD", 1)

anchor = '    _txt = (inbound_text or "").strip()'
insert = '''
    _p19p16 = _p19p16_confinement_domain_interceptor(inbound_text)
    if _p19p16:
        return _p19p9_universal_whatsapp_output_guard(inbound_text, _p19p16, "")
'''
if insert.strip() not in s:
    s = s.replace(anchor, insert + "\n" + anchor, 1)

p.write_text(s, encoding="utf-8")
