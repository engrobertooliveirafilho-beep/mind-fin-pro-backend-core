
import importlib
from app.runtime.forensic_trace import event, wrap_callable

TARGETS = [
    ("app.runtime.live_whatsapp_response", ["eldora_primary_runtime_reply", "live_whatsapp_response"]),
    ("app.runtime.universal_conversation_authority", ["universal_conversation_authority", "apply_universal_conversation_authority"]),
    ("app.runtime.factual_search_handoff", ["factual_search_handoff", "apply_factual_search_handoff"]),
    ("app.runtime.whatsapp_final_output_guard", ["whatsapp_final_output_guard", "apply_whatsapp_final_output_guard"]),
    ("app.runtime.final_conversational_arbiter", ["final_conversational_arbiter", "apply_final_conversational_arbiter"]),
    ("app.runtime.generic_conversation_state", ["get_state", "set_state", "clear_state"]),
    ("app.api.whatsapp", ["twiml", "webhook", "whatsapp_webhook"]),
]

def install():
    wrapped = []
    for mod_name, names in TARGETS:
        try:
            mod = importlib.import_module(mod_name)
        except Exception as e:
            event("FORENSIC_IMPORT_FAIL", module_name=mod_name, reply_after=repr(e))
            continue
        for name in names:
            if wrap_callable(mod, name, name.upper()):
                wrapped.append(f"{mod_name}.{name}")
    event("FORENSIC_BOOTSTRAP_INSTALLED", reply_after=wrapped, extra={"wrapped_count": len(wrapped)})
    return wrapped
