$ErrorActionPreference="Stop"

@"
from pathlib import Path
p=Path("app/main.py")
s=p.read_text(encoding="utf-8")

needle='''        body = m.group(1).strip()
        return f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{sanitize_final_human_output(sanitize_final_human_output(body))}</Message></Response>'
    return raw'''

patch='''        body = m.group(1).strip()
        try:
            body = p412n_final_semantic_ux_guard(message, body)
        except Exception:
            pass
        return f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{sanitize_final_human_output(sanitize_final_human_output(body))}</Message></Response>'
    try:
        raw_body = p412n_final_semantic_ux_guard(message, raw)
        return f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{sanitize_final_human_output(sanitize_final_human_output(raw_body))}</Message></Response>'
    except Exception:
        return raw'''

if needle not in s:
    raise SystemExit("NORMALIZE_TARGET_NOT_FOUND")

s=s.replace(needle,patch,1)
p.write_text(s,encoding="utf-8")
print("NORMALIZE_GUARD_PATCHED")
"@ | Set-Content "_patch_normalize_guard.py" -Encoding UTF8

python _patch_normalize_guard.py
python -m compileall -q app tests
pytest

python _replay_final_guard.py

git diff app/main.py
