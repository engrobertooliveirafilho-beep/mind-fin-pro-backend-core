
import functools, inspect, json, pathlib, datetime, traceback

TRACE_DIR = pathlib.Path("runtime_traces")
TRACE_DIR.mkdir(exist_ok=True)
TRACE_FILE = TRACE_DIR / "p51a_runtime_trace.jsonl"

def _safe(v, limit=900):
    try:
        s = repr(v)
    except Exception as e:
        s = f"<repr_error {e}>"
    return s[:limit]

def trace_event(stage, **data):
    row = {
        "ts": datetime.datetime.utcnow().isoformat() + "Z",
        "stage": stage,
        **data,
    }
    with TRACE_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\\n")

def trace_function(fn):
    if getattr(fn, "_p51a_traced", False):
        return fn

    async def _async(*args, **kwargs):
        trace_event("ENTER", function=f"{fn.__module__}.{fn.__qualname__}", args=_safe(args), kwargs=_safe(kwargs))
        try:
            out = await fn(*args, **kwargs)
            trace_event("EXIT", function=f"{fn.__module__}.{fn.__qualname__}", return_type=type(out).__name__, return_preview=_safe(out))
            return out
        except Exception as e:
            trace_event("ERROR", function=f"{fn.__module__}.{fn.__qualname__}", error=str(e), stack=traceback.format_exc())
            raise

    def _sync(*args, **kwargs):
        trace_event("ENTER", function=f"{fn.__module__}.{fn.__qualname__}", args=_safe(args), kwargs=_safe(kwargs))
        try:
            out = fn(*args, **kwargs)
            trace_event("EXIT", function=f"{fn.__module__}.{fn.__qualname__}", return_type=type(out).__name__, return_preview=_safe(out))
            return out
        except Exception as e:
            trace_event("ERROR", function=f"{fn.__module__}.{fn.__qualname__}", error=str(e), stack=traceback.format_exc())
            raise

    wrapped = functools.wraps(fn)(_async if inspect.iscoroutinefunction(fn) else _sync)
    wrapped._p51a_traced = True
    return wrapped
