from pathlib import Path

p = Path("app/runtime/cognitive_pipeline.py")
lines = p.read_text(encoding="utf-8").splitlines()
fixed = []
i = 0

while i < len(lines):
    line = lines[i]

    if line.startswith("if suppress_agricultural_contamination:"):
        i += 1
        while i < len(lines) and ("final[\"answer\"] = suppress_agricultural_contamination" in lines[i] or lines[i].strip() == ""):
            i += 1
        continue

    if line.startswith('save_message(user_id, "assistant", final["answer"])'):
        i += 1
        continue

    if line.startswith("    persist_state(user_id, state)"):
        fixed.append('    if suppress_agricultural_contamination:')
        fixed.append('        final["answer"] = suppress_agricultural_contamination(message, final.get("answer",""), str(intent))')
        fixed.append('    save_message(user_id, "assistant", final["answer"])')
        fixed.append(line)
        i += 1
        continue

    fixed.append(line)
    i += 1

p.write_text("\n".join(fixed) + "\n", encoding="utf-8")
