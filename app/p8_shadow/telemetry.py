import json
import time
import hashlib
from pathlib import Path
from typing import Any, Optional

DEFAULT_LOG_PATH = Path("_evidence") / "p8_shadow_execution_log.jsonl"

def stable_hash(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def append_shadow_log(
    *,
    request_id: str,
    module: str,
    status: str,
    latency_ms: float,
    execution_mode: str,
    result: Any = None,
    error: Optional[str] = None,
    log_path: Optional[str] = None,
) -> dict:
    path = Path(log_path) if log_path else DEFAULT_LOG_PATH
    path.parent.mkdir(parents=True, exist_ok=True)

    record = {
        "request_id": request_id,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "module": module,
        "latency_ms": latency_ms,
        "status": status,
        "result_hash": stable_hash(result),
        "error": error,
        "execution_mode": execution_mode,
        "runtime_version": "p8_shadow",
    }

    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return record
