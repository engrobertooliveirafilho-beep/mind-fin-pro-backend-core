$ErrorActionPreference="Stop"
$ts=Get-Date -Format "yyyyMMdd_HHmmss"
$ev="_evidence\FIX11K_C_SAFE_PROBE_$ts"
New-Item -ItemType Directory -Force $ev | Out-Null

try {
  git status --short | Out-File "$ev\STATUS_BEFORE.txt" -Encoding UTF8

@"
from __future__ import annotations
import contextvars, functools, inspect, json, time, uuid
from pathlib import Path

TRACE_DIR = Path("_evidence/FIX11K_RUNTIME_TRACE")
TRACE_DIR.mkdir(parents=True, exist_ok=True)
CID = contextvars.ContextVar("fix11k_cid", default=None)

def event(hop: str, **data):
    cid = CID.get() or ("no_request_" + uuid.uuid4().hex)
    payload = {"ts": time.time(), "cid": cid, "hop": hop, "data": {k: str(v)[:5000] for k,v in data.items()}}
    try:
        with (TRACE_DIR / f"{cid}.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        pass
    return payload

def wrap_callable(fn, hop=None):
    name = hop or getattr(fn, "__name__", "unknown")
    if getattr(fn, "_fix11k_wrapped", False):
        return fn
    if inspect.iscoroutinefunction(fn):
        @functools.wraps(fn)
        async def aw(*args, **kwargs):
            event("before_" + name, args=args, kwargs=kwargs)
            out = await fn(*args, **kwargs)
            event("after_" + name, output=out)
            return out
        aw._fix11k_wrapped = True
        return aw
    @functools.wraps(fn)
    def sw(*args, **kwargs):
        event("before_" + name, args=args, kwargs=kwargs)
        out = fn(*args, **kwargs)
        event("after_" + name, output=out)
        return out
    sw._fix11k_wrapped = True
    return sw

def install_fix11k_probe(ns):
    for t in [
        "dispatch_single_runtime",
        "p4_12_whatsapp_live_ux_guard",
        "p4_12_context_lock",
        "p4_12b_factual_execution_lock",
        "factual_search_handoff",
        "strategic_conversation_authority",
        "final_conversational_arbiter",
        "_p412n_normalize_xml_response",
        "twiml",
        "safe_reply",
    ]:
        if t in ns and callable(ns[t]):
            ns[t] = wrap_callable(ns[t], t)

    app = ns.get("app")
    if app and not getattr(app, "_fix11k_probe_installed", False):
        @app.middleware("http")
        async def fix11k_trace_middleware(request, call_next):
            if request.url.path != "/webhook/whatsapp":
                return await call_next(request)
            cid = uuid.uuid4().hex
            token = CID.set(cid)
            body = await request.body()
            event("inbound_request", route=request.url.path, body=body.decode("utf-8", "ignore"))
            response = await call_next(request)
            chunks = []
            async for chunk in response.body_iterator:
                chunks.append(chunk)
            content = b"".join(chunks)
            event("final_xml", status=response.status_code, body=content.decode("utf-8", "ignore"))
            CID.reset(token)
            from starlette.responses import Response
            return Response(content=content, status_code=response.status_code, headers=dict(response.headers), media_type=response.media_type)
        app._fix11k_probe_installed = True
"@ | Set-Content "app\runtime\fix11k_probe.py" -Encoding UTF8

@"
from pathlib import Path
p=Path("app/main.py")
s=p.read_text(encoding="utf-8")
block='''

# FIX11K_C_SAFE_PROBE_ACTIVE
try:
    from app.runtime.fix11k_probe import install_fix11k_probe
    install_fix11k_probe(globals())
except Exception:
    pass
'''
if "FIX11K_C_SAFE_PROBE_ACTIVE" not in s:
    s=s.rstrip()+block+"`n"
p.write_text(s,encoding="utf-8")
print("FIX11K_C_PATCHED")
"@ | Set-Content "_fix11k_c_patch.py" -Encoding UTF8

python _fix11k_c_patch.py
python -m compileall -q app tests
pytest

git add app/main.py app/runtime/fix11k_probe.py
git commit -m "fix11k c passive live hop probe"

$job = Start-Job -ScriptBlock {
  Set-Location "C:\Users\MindFin\Desktop\mind-fin-pro-backend-core"
  python -m uvicorn app.main:app --host 127.0.0.1 --port 8011
}
Start-Sleep -Seconds 8

$msgs=@("Oi","Tudo bem?","Quem é você?","Como você está?","Por que está dando erro?","Aprofunde","E depois?","Procure o erro principal","Quanto é 4x6")
$live=@()
foreach($m in $msgs){
  $r=Invoke-WebRequest -Method POST "http://127.0.0.1:8011/webhook/whatsapp" -Body @{Body=$m;From="whatsapp:+559999999999"} -ContentType "application/x-www-form-urlencoded"
  $live += [pscustomobject]@{message=$m;status=$r.StatusCode;response=$r.Content}
}
$live | ConvertTo-Json -Depth 20 | Out-File "$ev\REAL_HOP_TRACE.json" -Encoding UTF8

Stop-Job $job -ErrorAction SilentlyContinue
Remove-Job $job -Force -ErrorAction SilentlyContinue

Copy-Item "_evidence\FIX11K_RUNTIME_TRACE\*" $ev -Force -ErrorAction SilentlyContinue

@{
  export_ready=$true
  p412n_c="OPEN"
  branch=(git branch --show-current)
  commit=(git rev-parse --short HEAD)
  status="FIX11K_C_TRACE_CAPTURED_LOCAL"
  note="Probe passivo aplicado em branch isolada. UX não corrigida."
} | ConvertTo-Json -Depth 10 | Out-File "$ev\FINAL_TRUTH_LEDGER.json" -Encoding UTF8

rclone copy $ev "gdrive:MIND/CONTROL/FIX11K_C_SAFE_PROBE_$ts" --progress
git status
Write-Host "FIX11K_C_DONE evidence=$ev"

} catch {
  Write-Host "ABORT_FIX11K_C => $($_.Exception.Message)"
  git reset --hard 80ecc1b
  git clean -fd
  throw
}
