from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class StudioConfig:
    repo_root: Path
    runtime_root: Path
    downloads_root: Path
    media_config: Path
    brain_config: Path
    drive_folder_id: str
    review_required: bool
    auto_publish: bool
    auto_delete_local: bool

    @classmethod
    def load(cls, path: Path) -> "StudioConfig":
        data = json.loads(path.read_text(encoding="utf-8"))
        repo_root = Path(__file__).resolve().parents[2]
        return cls(
            repo_root=repo_root,
            runtime_root=repo_root / data["runtime_root"],
            downloads_root=Path(data["downloads_root"]),
            media_config=repo_root / data["media_config"],
            brain_config=repo_root / data["brain_config"],
            drive_folder_id=data["drive_folder_id"],
            review_required=bool(data["review_required"]),
            auto_publish=bool(data["auto_publish"]),
            auto_delete_local=bool(data["auto_delete_local"]),
        )