from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class TaskQueue:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.pending = root / "pending"
        self.running = root / "running"
        self.done = root / "done"
        self.failed = root / "failed"
        for path in (self.pending, self.running, self.done, self.failed):
            path.mkdir(parents=True, exist_ok=True)

    def enqueue(self, task_type: str, payload: dict[str, Any]) -> Path:
        task_id = f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{uuid.uuid4().hex[:10]}"
        task = {
            "schema": "eldora.ai.studio.task.v1",
            "task_id": task_id,
            "task_type": task_type,
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "payload": payload,
            "status": "PENDING",
        }
        path = self.pending / f"{task_id}.json"
        path.write_text(json.dumps(task, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def counts(self) -> dict[str, int]:
        return {
            "pending": len(list(self.pending.glob("*.json"))),
            "running": len(list(self.running.glob("*.json"))),
            "done": len(list(self.done.glob("*.json"))),
            "failed": len(list(self.failed.glob("*.json"))),
        }