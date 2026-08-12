from pathlib import Path

p = Path("app/runtime/cognitive_pipeline.py")
s = p.read_text(encoding="utf-8")

imp = """
# P19P5_AUTOMOTIVE_ROUTER_CORRECTION
try:
    from app.runtime.automotive_domain_guard import automotive_domain_override, suppress_agricultural_contamination
except Exception:
    automotive_domain_override = None
    suppress_agricultural_contamination = None
# /P19P5_AUTOMOTIVE_ROUTER_CORRECTION
"""

if "P19P5_AUTOMOTIVE_ROUTER_CORRECTION" not in s:
    anchor = "from app.runtime.intent_router import route_intent"
    s = s.replace(anchor, anchor + imp, 1)

# depois de route_intent(...)
targets = [
    "intent = route_intent(message)",
    "intent=route_intent(message)",
]

for t in targets:
    if t in s and "automotive_domain_override(message, intent" not in s:
        s = s.replace(
            t,
            t + """
    if automotive_domain_override:
        intent = automotive_domain_override(message, intent)
""",
            1
        )

# antes de salvar/retornar final["answer"]
target2 = 'save_message(user_id, "assistant", final["answer"])'
if target2 in s and "suppress_agricultural_contamination(message, final" not in s:
    s = s.replace(
        target2,
        """
    if suppress_agricultural_contamination:
        final["answer"] = suppress_agricultural_contamination(message, final.get("answer",""), str(intent))
""" + target2,
        1
    )

p.write_text(s, encoding="utf-8")
