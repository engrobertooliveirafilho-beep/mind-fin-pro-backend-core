from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class ContentSpec:
    content_id: str
    channel: str
    format: str
    scene: str
    objective: str
    image_prompt: str
    video_prompt: str
    overlay_text: str
    caption: str
    cta: str
    negative_prompt: str
    status: str = "PLANNED"


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )


def write_batch_manifest(path: Path, batch_id: str, items: list[ContentSpec], canon: list[dict[str, Any]]) -> None:
    write_json(
        path,
        {
            "schema": "eldora.media.batch.v1",
            "batch_id": batch_id,
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "canon_assets": canon,
            "items": [asdict(item) for item in items],
        },
    )