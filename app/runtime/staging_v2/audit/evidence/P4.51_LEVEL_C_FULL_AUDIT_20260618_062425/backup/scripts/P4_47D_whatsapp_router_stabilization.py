from pathlib import Path

p = Path("app/api/whatsapp.py")
txt = p.read_text(encoding="utf-8")

old = '''        visible = run_cognitive_pipeline(sender_id, expanded_message)
    return visible.get("answer","") if isinstance(visible, dict) else str(visible)
'''

new = '''        visible = run_cognitive_pipeline(sender_id, expanded_message)

    if "visible" not in locals() or visible is None:
        visible = run_cognitive_pipeline(sender_id, inbound_text)

    return visible.get("answer","") if isinstance(visible, dict) else str(visible)
'''

if old not in txt:
    raise SystemExit("TARGET_BLOCK_NOT_FOUND")

txt = txt.replace(old, new, 1)
p.write_text(txt, encoding="utf-8")

print("P4.47D whatsapp router stabilization applied")
