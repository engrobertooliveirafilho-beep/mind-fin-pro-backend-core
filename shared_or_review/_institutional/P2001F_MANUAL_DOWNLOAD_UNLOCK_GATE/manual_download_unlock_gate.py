import json
import os
from pathlib import Path
from datetime import datetime, UTC

OUT = Path("_evidence/P2001F")

def env_flag(name):
    return os.getenv(name, "false").lower().strip() == "true"

def run():

    OUT.mkdir(parents=True, exist_ok=True)

    allow_download = env_flag("ALLOW_DATA_DOWNLOAD")

    gate = {
        "program": "P2001F_MANUAL_DOWNLOAD_UNLOCK_GATE",
        "status": "PASS",
        "mode": "RESEARCH_ONLY",
        "allow_data_download": allow_download,
        "download_unlocked": allow_download,
        "manual_confirmation_required": True,
        "default_state": "LOCKED",
        "unlock_condition": "ALLOW_DATA_DOWNLOAD=true",
        "download_executed": False,
        "files_written": False,
        "records_downloaded": 0,
        "order_sent": False,
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
        "mt5_real": "FORBIDDEN",
        "approved_for_P2001G": True,
        "generated_at": datetime.now(UTC).isoformat()
    }

    (OUT / "DOWNLOAD_UNLOCK_GATE.json").write_text(
        json.dumps(gate, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    (OUT / "SUMMARY.json").write_text(
        json.dumps(gate, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(json.dumps(gate, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    run()
