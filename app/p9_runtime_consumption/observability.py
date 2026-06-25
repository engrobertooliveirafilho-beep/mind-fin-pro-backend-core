import json
import time
from pathlib import Path
from typing import Any, Dict

def append_p9_observation(record: Dict[str, Any], log_path: str) -> Dict[str, Any]:
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    enriched = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        **record,
    }

    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(enriched, ensure_ascii=False) + "\n")

    return enriched
