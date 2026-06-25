from app.api import whatsapp as w

def p19_unified_pipeline(inbound_text, sender_id, context, out):

    normalized = w._p19p5_block_agricultural_automotive_contamination(
        inbound_text, out, context
    )

    cleaned = w._p19p6_expand_bad_followup_template(
        inbound_text, normalized, context
    )

    expanded = w._p19p7_contextual_followup_expansion(
        inbound_text, cleaned, context
    )

    final = w._p19p8_suppress_generic_restart(
        inbound_text, expanded, context
    )

    return final
