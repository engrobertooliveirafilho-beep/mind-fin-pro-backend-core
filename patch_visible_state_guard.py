from pathlib import Path

p=Path("app/api/whatsapp.py")
lines=p.read_text(encoding="utf-8").splitlines()

import_line="from app.runtime.mind_state_visible_context import is_state_query, build_mind_state_visible_response"
if import_line not in lines:
    for i,l in enumerate(lines):
        if "from app.runtime.cognitive_pipeline import run_cognitive_pipeline" in l:
            lines.insert(i+1, import_line)
            break

out=[]
inserted=False

for line in lines:
    out.append(line)
    if line.startswith("def eldora_primary_runtime_reply(") and not inserted:
        out.append("")
        out.append("    if is_state_query(inbound_text):")
        out.append("        return build_mind_state_visible_response()")
        inserted=True

if not inserted:
    raise RuntimeError("eldora_primary_runtime_reply not found")

p.write_text("\n".join(out)+"\n",encoding="utf-8")
