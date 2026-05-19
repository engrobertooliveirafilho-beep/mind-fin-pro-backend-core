from pathlib import Path

p=Path("app/api/whatsapp.py")
s=p.read_text(encoding="utf-8")

imp="from app.runtime.mind_state_visible_context import is_state_query, build_mind_state_visible_response"
if imp not in s:
    anchor="from app.runtime.cognitive_pipeline import run_cognitive_pipeline"
    if anchor in s:
        s=s.replace(anchor, anchor+"\n"+imp)
    else:
        s=imp+"\n"+s

if "PROD_STATE_GUARD_DIRECT" not in s:
    lines=s.splitlines()
    out=[]
    inserted=False

    for i,line in enumerate(lines):
        out.append(line)

        if "await request.form()" in line and not inserted:
            indent=line[:len(line)-len(line.lstrip())]
            out.append("")
            out.append(indent+"# PROD_STATE_GUARD_DIRECT")
            out.append(indent+"__eldora_body = str((form.get('Body') or form.get('body') or form.get('message') or ''))")
            out.append(indent+"if is_state_query(__eldora_body):")
            out.append(indent+"    return twiml(build_mind_state_visible_response())")
            inserted=True

    if not inserted:
        raise RuntimeError("REQUEST_FORM_PATTERN_NOT_FOUND")

    s="\n".join(out)+"\n"

p.write_text(s,encoding="utf-8")
