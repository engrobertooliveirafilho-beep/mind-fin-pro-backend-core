$ErrorActionPreference="Stop"

@"
from pathlib import Path

p=Path("app/main.py")
s=p.read_text(encoding="utf-8")

target='return f\'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{sanitize_final_human_output(sanitize_final_human_output(body))}</Message></Response>\''

replace='''try:
            body = p412n_final_semantic_ux_guard(message, body)
        except Exception:
            pass
        return f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{sanitize_final_human_output(sanitize_final_human_output(body))}</Message></Response>' '''

if "body = p412n_final_semantic_ux_guard(message, body)" not in s:
    if target not in s:
        raise SystemExit("NORMALIZE_RETURN_NOT_FOUND")
    s=s.replace(target,replace,1)

p.write_text(s,encoding="utf-8")
print("NORMALIZE_PATCH_OK")
"@ | Set-Content "_force_patch_normalize.py" -Encoding UTF8

python _force_patch_normalize.py
python -m compileall -q app tests
pytest
python _replay_final_guard.py

Select-String -Path "app\main.py" -Pattern "p412n_final_semantic_ux_guard\(message, body\)" | Select-Object LineNumber,Line
git diff app/main.py
