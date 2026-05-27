from pathlib import Path
import re

p=Path("app/main.py")
s=p.read_text(encoding="utf-8")

start=s.find("def _p412n_normalize_xml_response")
end=s.find("@app.post(\"/webhook/whatsapp\")", start)

if start < 0 or end < 0:
    raise SystemExit("NORMALIZE_BLOCK_NOT_FOUND")

new_block='''def _p412n_normalize_xml_response(message: str, xml: str) -> str:
    import re
    raw = str(xml or "")
    m = re.search(r"<Message>(.*?)</Message>", raw, flags=re.S)
    body = m.group(1).strip() if m else raw.strip()
    return f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{sanitize_final_human_output(sanitize_final_human_output(body))}</Message></Response>'

'''

s=s[:start]+new_block+s[end:]
p.write_text(s,encoding="utf-8")
print("NORMALIZE_SERIALIZER_ONLY_OK")
