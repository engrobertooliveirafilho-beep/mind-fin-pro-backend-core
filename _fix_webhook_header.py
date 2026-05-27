from pathlib import Path

p = Path("app/main.py")
lines = p.read_text(encoding="utf-8").splitlines()

start = 402   # linha 403
end = 418     # remove até 418

new_block = [
    '@app.post("/webhook/whatsapp")',
    'async def whatsapp_webhook(request: Request):',
    '    # FIX11K_TRACE_ACTIVE',
    '    _fix11k_trace = None',
    '    try:',
    '        _fix11k_trace = new_trace(',
    '            "POST /webhook/whatsapp",',
    '            "",',
    '            ""',
    '        )',
    '        mark(_fix11k_trace, "route", "POST /webhook/whatsapp")',
    '    except Exception:',
    '        pass'
]

fixed = lines[:start] + new_block + lines[end:]
p.write_text("\n".join(fixed) + "\n", encoding="utf-8")

print("WEBHOOK_HEADER_REBUILT_OK")
