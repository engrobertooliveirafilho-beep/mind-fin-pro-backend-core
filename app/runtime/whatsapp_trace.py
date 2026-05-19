from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import json

TRACE_FILE = Path("whatsapp_handler_trace_last.json")

def write_trace(stage: str, data: dict | None = None) -> None:
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "stage": stage,
        "data": data or {}
    }
    TRACE_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
