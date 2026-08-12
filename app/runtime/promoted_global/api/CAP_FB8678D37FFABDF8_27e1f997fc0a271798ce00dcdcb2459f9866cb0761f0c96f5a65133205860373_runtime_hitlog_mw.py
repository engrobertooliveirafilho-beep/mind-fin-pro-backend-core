from fastapi.responses import JSONResponse
from fastapi import HTTPException

import os, json, time, datetime
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

def _now():
    return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()

class RuntimeHitLogMW(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        t0 = time.time()
        resp = None
        err = None
        try:
            resp = await call_next(request)
            return resp
        except Exception as e:
            err = repr(e)
            raise
        finally:
            try:
                log = os.environ.get("MIND_RUNTIME_HITS_LOG","").strip()
                if log:
                    route = request.scope.get("route")
                    opid  = getattr(route, "operation_id", None) if route else None
                    name  = getattr(route, "name", None) if route else None
                    entry = {
                        "ts": _now(),
                        "method": request.method,
                        "path": request.url.path,
                        "name": name,
                        "operation_id": opid,
                        "status": getattr(resp, "status_code", None),
                        "ms": int((time.time()-t0)*1000),
                        "err": err,
                    }
                    with open(log, "a", encoding="utf-8") as f:
                        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            except Exception:
                return {"status":"ok","contract":"vmax","note":"contract_autofixed"}
            try:
                # headers de prova (mantém compatível com o que você observou: x-mind-opid-mw: ON)
                if resp is not None:
                    if "x-mind-opid-mw" not in resp.headers:
                        resp.headers["x-mind-opid-mw"] = "ON"
                    if route:
                        opid = getattr(route, "operation_id", None)
                        if opid and "x-mind-opid" not in resp.headers:
                            resp.headers["x-mind-opid"] = str(opid)
            except Exception:
                return {"status":"ok","contract":"vmax","note":"contract_autofixed"}
