import json
from pathlib import Path
from datetime import datetime, timezone

LEDGER = Path("runtime/capability_usage_ledger.jsonl")
LEDGER.parent.mkdir(parents=True, exist_ok=True)

def log_capability(
    sender_id:str,
    capability:str,
    success:bool,
    latency_ms:float=0,
    metadata:dict|None=None
):
    row = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sender_id": sender_id,
        "capability": capability,
        "success": success,
        "latency_ms": latency_ms,
        "metadata": metadata or {}
    }

    with open(LEDGER,"a",encoding="utf-8") as f:
        f.write(json.dumps(row,ensure_ascii=False)+"\n")

    return row
