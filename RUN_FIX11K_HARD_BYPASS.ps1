$ErrorActionPreference="Stop"

@"
from pathlib import Path
import re

p=Path("app/main.py")
s=p.read_text(encoding="utf-8")

# 1. limpar código morto duplicado após primeiro return out
pat=r"(def p412n_final_semantic_ux_guard\(.*?return out)\n(?:.|\n)*?\n@app.post"
m=re.search(pat,s,re.S)
if not m:
    raise SystemExit("GUARD_BLOCK_NOT_FOUND")

clean_guard=m.group(1)+"\n\n@app.post"
s=s[:m.start()] + clean_guard + s[m.end():]

# 2. bypass ACA antes do authority/arbiter
anchor='primary_reply = factual_search_handoff(primary_reply, message)'
inject='''primary_reply = factual_search_handoff(primary_reply, message)

            runtime_error_reply = any(x in str(primary_reply) for x in [
                "WEBHOOK_ERROR_TOTAL",
                "DATABASE_URL missing",
                "AssertionError",
                "Traceback"
            ])

            if runtime_error_reply:
                primary_reply = p412n_final_semantic_ux_guard(message, primary_reply)
                return Response(
                    content=_p412n_normalize_xml_response(message, primary_twiml(primary_reply)),
                    media_type="application/xml"
                )'''

if "return Response(" not in s[s.find(anchor):s.find(anchor)+1200]:
    s=s.replace(anchor,inject,1)

# 3. kill-switch final
s=s.replace(
'primary_reply = p412n_final_semantic_ux_guard(message, primary_reply)',
'''primary_reply = p412n_final_semantic_ux_guard(message, primary_reply)
            if "vamos aprofundar sem reiniciar" in str(primary_reply).lower():
                primary_reply = p412n_final_semantic_ux_guard(message, "")''',
1
)

p.write_text(s,encoding="utf-8")
print("FIX11K_HARD_RUNTIME_BYPASS_OK")
"@ | Set-Content "_fix11k_hard_bypass.py" -Encoding UTF8

python _fix11k_hard_bypass.py
python -m compileall -q app tests
pytest
python _replay_final_guard.py
git diff app/main.py
