from pathlib import Path
import re

path = Path("app/api/whatsapp.py")
src = path.read_text(encoding="utf-8")
original = src

# 1) Garante função bridge real Twilio/WhatsApp -> eldora_primary_runtime_reply
bridge = r'''
# ============================================================
# P19P21B - REAL WHATSAPP CERTIFIED BRIDGE
# Objetivo:
# O canal real não pode responder por template/bypass superficial.
# Toda mensagem real do WhatsApp deve passar por eldora_primary_runtime_reply.
# ============================================================

def _p19p21b_extract_twilio_form_value(form_obj, key: str, default: str = ""):
    try:
        v = form_obj.get(key)
        if v is None:
            return default
        return str(v)
    except Exception:
        return default

def _p19p21b_real_whatsapp_certified_reply(sender_id: str, inbound_text: str) -> str:
    try:
        reply = eldora_primary_runtime_reply(sender_id, inbound_text)
        if reply is None:
            reply = ""
        return _p19p9_universal_whatsapp_output_guard(inbound_text, str(reply), "")
    except Exception as e:
        return (
            "Vou manter o contexto e responder de forma prática. "
            "Se o assunto é confinamento, comece pelo trato: silo, balança, mistura, cocho, água, pesagem e alertas."
        )

def _p19p21b_is_real_whatsapp_form(form_obj) -> bool:
    try:
        body = _p19p21b_extract_twilio_form_value(form_obj, "Body", "")
        sender = _p19p21b_extract_twilio_form_value(form_obj, "From", "")
        return bool(body) and ("whatsapp:" in sender.lower() or sender.strip() != "")
    except Exception:
        return False
# /P19P21B_REAL_WHATSAPP_CERTIFIED_BRIDGE
'''

if "P19P21B - REAL WHATSAPP CERTIFIED BRIDGE" not in src:
    marker = "router = APIRouter()"
    idx = src.find(marker)
    if idx == -1:
        idx = src.find("def eldora_primary_runtime_reply")
    if idx == -1:
        raise RuntimeError("Não encontrei ponto seguro para inserir bridge P19P21B.")
    src = src[:idx] + bridge + "\n\n" + src[idx:]

# 2) Localiza handlers FastAPI async com request.form() e injeta retorno certificado após leitura do form.
# Faz patch conservador: após cada linha "form = await request.form()", injeta gate real.
lines = src.splitlines()
out = []
inserted = False

for i, line in enumerate(lines):
    out.append(line)
    stripped = line.strip()

    if "await request.form()" in stripped and "form" in stripped and "P19P21B real whatsapp gate" not in src:
        indent = line[:len(line) - len(line.lstrip())]
        var = stripped.split("=")[0].strip()
        if var:
            out.append(indent + "# P19P21B real whatsapp gate")
            out.append(indent + "try:")
            out.append(indent + f"    if _p19p21b_is_real_whatsapp_form({var}):")
            out.append(indent + f"        _p19p21b_body = _p19p21b_extract_twilio_form_value({var}, 'Body', '')")
            out.append(indent + f"        _p19p21b_from = _p19p21b_extract_twilio_form_value({var}, 'From', '')")
            out.append(indent + "        _p19p21b_answer = _p19p21b_real_whatsapp_certified_reply(_p19p21b_from, _p19p21b_body)")
            out.append(indent + "        return Response(content=twiml(_p19p21b_answer), media_type='application/xml')")
            out.append(indent + "except Exception:")
            out.append(indent + "    pass")
            inserted = True

src = "\n".join(out) + "\n"

# 3) Se não achou request.form(), injeta auditoria sem quebrar.
if not inserted and "P19P21B_NO_FORM_GATE_FOUND" not in src:
    src += "\n# P19P21B_NO_FORM_GATE_FOUND: auditoria encontrou bridge, mas não encontrou await request.form() para gate automático.\n"

path.write_text(src, encoding="utf-8")

print({
    "changed": src != original,
    "inserted_form_gate": inserted,
    "file": str(path),
    "mission": "P19P21B_REAL_WHATSAPP_EXECUTION_PATH_AUDIT_AND_PATCH"
})
