from pathlib import Path

p=Path("app/api/whatsapp.py")
s=p.read_text(encoding="utf-8")

if "whatsapp_intelligence_activation" not in s:
    s=s.replace(
        "from app.runtime.cognitive_pipeline import run_cognitive_pipeline",
        "from app.runtime.cognitive_pipeline import run_cognitive_pipeline\nfrom app.runtime.whatsapp_intelligence_activation import enrich_whatsapp_context, whatsapp_intelligence_active"
    )

needle="visible = run_cognitive_pipeline(\n        sender_id,\n        inbound_text\n    )"

insert="""visible = run_cognitive_pipeline(
        sender_id,
        inbound_text
    )

    if whatsapp_intelligence_active() and isinstance(visible, dict):
        visible["activation_context"] = enrich_whatsapp_context(sender_id, inbound_text, {})"""

if needle in s and "activation_context" not in s:
    s=s.replace(needle, insert)

p.write_text(s,encoding="utf-8")
