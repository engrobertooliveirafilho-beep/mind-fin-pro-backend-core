from pathlib import Path

p = Path("app/runtime/cognitive_pipeline.py")
txt = p.read_text(encoding="utf-8")

if "P4_47C_LEVEL_A_REAL_CONSUMPTION" not in txt:
    needle = "    strategy = build_response_strategy(intent, state, memory)\n\n    raw = build_response(message, intent, memory, state, persona, strategy)"
    patch = '''    strategy = build_response_strategy(intent, state, memory)

    # P4_47C_LEVEL_A_REAL_CONSUMPTION
    try:
        from app.runtime.level_a_cognitive_shadow import run_level_a_shadow
        level_a = run_level_a_shadow(message=message, sender_id=user_id, context=memory)
        memory["level_a"] = level_a
        memory["cognitive_hints"] = level_a.get("signals", [])
        memory["diagnostic_recommendation"] = level_a.get("recommendation")
    except Exception as exc:
        memory["level_a"] = {"status": "failed", "error": str(exc)}
        memory["cognitive_hints"] = []

    raw = build_response(message, intent, memory, state, persona, strategy)'''
    if needle not in txt:
        raise SystemExit("needle_not_found")
    txt = txt.replace(needle, patch, 1)

p.write_text(txt, encoding="utf-8")
print("P4.47C Level A real consumption patch applied")
