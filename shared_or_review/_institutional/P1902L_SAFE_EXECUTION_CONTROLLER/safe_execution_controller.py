from __future__ import annotations

import json
import os
from pathlib import Path
from datetime import datetime, UTC


OUT = Path("_evidence/P1902L")

REQUIRED = [
    "_evidence/P1902F/DOWNLOAD_JOBS.json",
    "_evidence/P1902F/NORMALIZATION_JOBS.json",
    "_evidence/P1902G/SOURCE_RANKING.json",
    "_evidence/P1902J/EXECUTION_READINESS_GATE.json",
    "_evidence/P1902K/DRY_RUN_EXECUTION_SIMULATOR.json",
]


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def env_bool(name: str) -> bool:
    return os.getenv(name, "false").strip().lower() == "true"


def run():
    OUT.mkdir(parents=True, exist_ok=True)

    allow_data_download = env_bool("ALLOW_DATA_DOWNLOAD")
    allow_broker_connection = env_bool("ALLOW_BROKER_CONNECTION")
    allow_live_trading = env_bool("ALLOW_LIVE_TRADING")
    allow_real_orders = env_bool("ALLOW_REAL_ORDERS")

    checks = []
    blockers = []

    for item in REQUIRED:
        p = Path(item)
        exists = p.exists()
        checks.append({"path": item, "exists": exists})
        if not exists:
            blockers.append(f"MISSING:{item}")

    downloads = read_json(Path("_evidence/P1902F/DOWNLOAD_JOBS.json")) or []
    normalizations = read_json(Path("_evidence/P1902F/NORMALIZATION_JOBS.json")) or []

    if len(downloads) != len(normalizations):
        blockers.append("DOWNLOAD_NORMALIZATION_JOB_MISMATCH")

    if allow_broker_connection:
        blockers.append("BROKER_CONNECTION_NOT_ALLOWED")

    if allow_live_trading:
        blockers.append("LIVE_TRADING_NOT_ALLOWED")

    if allow_real_orders:
        blockers.append("REAL_ORDERS_NOT_ALLOWED")

    controller_ready = len(blockers) == 0 and len(downloads) > 0

    result = {
        "program": "P1902L_SAFE_EXECUTION_CONTROLLER",
        "status": "PASS" if controller_ready else "BLOCKED",
        "mode": "RESEARCH_ONLY",
        "allow_data_download": allow_data_download,
        "allow_broker_connection": allow_broker_connection,
        "allow_live_trading": allow_live_trading,
        "allow_real_orders": allow_real_orders,
        "order_sent": False,
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
        "mt5_real": "FORBIDDEN",
        "download_jobs": len(downloads),
        "normalization_jobs": len(normalizations),
        "checks": checks,
        "blockers": blockers,
        "controller_ready": controller_ready,
        "approved_for_P1903": controller_ready,
        "generated_at": datetime.now(UTC).isoformat(),
    }

    (OUT / "SAFE_EXECUTION_CONTROLLER.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    (OUT / "SUMMARY.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    run()
