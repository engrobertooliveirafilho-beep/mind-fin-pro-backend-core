from pathlib import Path
p=Path("app/main.py")
s=p.read_text(encoding="utf-8")

start=s.find("def _p412n_normalize_xml_response")
end=s.find("def p412n_final_semantic_ux_guard", start)
if start < 0 or end < 0:
    raise SystemExit("NORMALIZE_BLOCK_NOT_FOUND")

new_block=r'''def _p412n_normalize_xml_response(message: str, xml: str) -> str:
    import re
    raw = str(xml or "")
    m = re.search(r"<Message>(.*?)</Message>", raw, re.S)
    body = m.group(1).strip() if m else raw.strip()
    try:
        body = p412n_final_semantic_ux_guard(message, body)
    except Exception:
        pass
    return f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{sanitize_final_human_output(sanitize_final_human_output(body))}</Message></Response>'

'''

s=s[:start]+new_block+s[end:]
p.write_text(s,encoding="utf-8")
print("NORMALIZE_REBUILT_SAFE")
