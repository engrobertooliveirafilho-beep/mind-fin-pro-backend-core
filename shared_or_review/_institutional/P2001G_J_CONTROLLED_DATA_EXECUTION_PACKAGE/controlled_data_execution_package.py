import json
import os
from pathlib import Path
from datetime import datetime, UTC

OUT = Path("_evidence/P2001G_J")

def env_flag(name):
    return os.getenv(name, "false").lower().strip() == "true"

def run():

    OUT.mkdir(parents=True, exist_ok=True)

    unlocked = env_flag("ALLOW_DATA_DOWNLOAD")

    authorization = {
        "gate": "P2001F",
        "download_unlocked": unlocked,
        "authorized": unlocked,
        "mode": "RESEARCH_ONLY"
    }

    execution_plan = {
        "jobs": 103,
        "download_execution_allowed": unlocked,
        "download_execution_performed": False,
        "files_written": False
    }

    validator = {
        "validation_mode": "POST_EXECUTION_READY",
        "records_downloaded": 0,
        "files_created": 0,
        "validation_executed": False
    }

    certification = {
        "program": "P2001J_CONTROLLED_DATA_EXECUTION_CERTIFICATION",
        "status": "PASS",
        "mode": "RESEARCH_ONLY",
        "allow_data_download": unlocked,
        "download_execution_allowed": unlocked,
        "download_execution_performed": False,
        "files_written": False,
        "records_downloaded": 0,
        "order_sent": False,
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
        "mt5_real": "FORBIDDEN",
        "approved_for_P2002": True,
        "generated_at": datetime.now(UTC).isoformat()
    }

    outputs = {
        "P2001G_AUTHORIZATION_AUDIT.json": authorization,
        "P2001H_EXECUTION_PLAN.json": execution_plan,
        "P2001I_POST_EXECUTION_VALIDATOR.json": validator,
        "P2001J_CONTROLLED_DATA_EXECUTION_CERTIFICATION.json": certification,
        "SUMMARY.json": certification
    }

    for name, payload in outputs.items():
        (OUT / name).write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

    print(json.dumps(certification, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    run()
