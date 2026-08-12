from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class StudioState:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {
                "schema": "eldora.ai.studio.state.v1",
                "created_at_utc": datetime.now(timezone.utc).isoformat(),
                "last_research_run": None,
                "last_candidate": None,
                "last_approved_asset": None,
                "last_error": None,
            }
        return json.loads(self.path.read_text(encoding="utf-8"))

    def save(self, payload: dict[str, Any]) -> None:
        payload["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
        self.path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )