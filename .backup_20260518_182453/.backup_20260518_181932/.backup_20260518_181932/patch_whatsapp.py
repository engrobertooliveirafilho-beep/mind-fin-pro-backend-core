from pathlib import Path

p=Path("app/main.py")
txt=p.read_text(encoding="utf-8")

new_code = r'''
from fastapi import Request

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):

    payload = {}

    try:
        ctype = request.headers.get("content-type","")

        if "application/json" in ctype:
            payload = await request.json()
        else:
            form = await request.form()
            payload = dict(form)

    except Exception as e:
        payload = {"parser_error": str(e)}

    sender_id = (
        payload.get("From")
        or payload.get("from")
        or payload.get("sender_id")
        or "unknown"
    )

    message = (
        payload.get("Body")
        or payload.get("body")
        or payload.get("message")
        or ""
    )

    return {
        "status":"ok",
        "sender_id":sender_id,
        "message":message,
        "payload":payload
    }
'''

start = txt.find('@app.post("/webhook/whatsapp")')

if start == -1:
    raise Exception("webhook endpoint nao encontrado")

txt = txt[:start] + new_code

p.write_text(txt,encoding="utf-8")

print("PATCH_OK")
