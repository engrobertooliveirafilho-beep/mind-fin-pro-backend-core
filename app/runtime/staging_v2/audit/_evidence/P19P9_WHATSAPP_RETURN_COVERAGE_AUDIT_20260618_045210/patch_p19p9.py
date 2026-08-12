from pathlib import Path

p = Path("app/api/whatsapp.py")
s = p.read_text(encoding="utf-8")

helper = '''
# P19P9_UNIVERSAL_WHATSAPP_OUTPUT_GUARD
def _p19p9_universal_whatsapp_output_guard(inbound_text: str, answer: str, context: str = "") -> str:
    out = str(answer or "")
    try:
        if "_p19p3_apply_automotive_guards" in globals():
            out = _p19p3_apply_automotive_guards(inbound_text, out, context)
    except Exception:
        pass
    try:
        if "_p19p8_suppress_generic_restart" in globals():
            out = _p19p8_suppress_generic_restart(inbound_text, out, context)
    except Exception:
        pass
    try:
        if "_p19p7_contextual_followup_expansion" in globals():
            out = _p19p7_contextual_followup_expansion(inbound_text, out, context)
    except Exception:
        pass
    try:
        if "_p19p6_expand_bad_followup_template" in globals():
            out = _p19p6_expand_bad_followup_template(inbound_text, out, context)
    except Exception:
        pass
    return out
# /P19P9_UNIVERSAL_WHATSAPP_OUTPUT_GUARD
'''

if "P19P9_UNIVERSAL_WHATSAPP_OUTPUT_GUARD" not in s:
    anchor = "# P19P8_GENERIC_RESTART_SUPPRESSION"
    s = s.replace(anchor, helper + "\n" + anchor, 1)

# Patch returns críticos com texto direto dentro de eldora_primary_runtime_reply.
replacements = {
    'return _guard_reply': 'return _p19p9_universal_whatsapp_output_guard(inbound_text, _guard_reply, "")',
    'return _contract_reply': 'return _p19p9_universal_whatsapp_output_guard(inbound_text, _contract_reply, "")',
    'return _followup_reply': 'return _p19p9_universal_whatsapp_output_guard(inbound_text, _followup_reply, "")',
    'return build_mind_state_visible_response()': 'return _p19p9_universal_whatsapp_output_guard(inbound_text, build_mind_state_visible_response(), "")',
}

for old, new in replacements.items():
    s = s.replace(old, new)

# Patch retorno direto do visible, caso alguma versão ainda exista.
s = s.replace(
    'return visible.get("answer","") if isinstance(visible, dict) else str(visible)',
    'return _p19p9_universal_whatsapp_output_guard(inbound_text, visible.get("answer","") if isinstance(visible, dict) else str(visible), str(visible))'
)

s = s.replace(
    'return str(visible.get("answer","")) if isinstance(visible,dict) else str(visible)',
    'return _p19p9_universal_whatsapp_output_guard(inbound_text, str(visible.get("answer","")) if isinstance(visible,dict) else str(visible), str(visible))'
)

p.write_text(s, encoding="utf-8")
