from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    repo_root: Path
    runtime_root: Path
    canon_root: Path
    output_root: Path
    evidence_root: Path
    image_generator_cmd: str | None
    video_generator_cmd: str | None
    identity_validator_cmd: str | None

    @classmethod
    def load(cls, config_path: Path | None = None) -> "Settings":
        repo_root = Path(__file__).resolve().parents[2]
        data: dict[str, object] = {}

        if config_path and config_path.exists():
            data = json.loads(config_path.read_text(encoding="utf-8"))

        runtime_root = repo_root / str(data.get("runtime_root", "runtime/eldora_media"))
        canon_root = repo_root / str(data.get("canon_root", "runtime/eldora_media/canon_cache"))
        output_root = repo_root / str(data.get("output_root", "runtime/eldora_media/output"))
        evidence_root = repo_root / str(data.get("evidence_root", "runtime/evidence/eldora_media"))

        return cls(
            repo_root=repo_root,
            runtime_root=runtime_root,
            canon_root=canon_root,
            output_root=output_root,
            evidence_root=evidence_root,
            image_generator_cmd=os.getenv("ELDORA_IMAGE_GENERATOR_CMD"),
            video_generator_cmd=os.getenv("ELDORA_VIDEO_GENERATOR_CMD"),
            identity_validator_cmd=os.getenv("ELDORA_IDENTITY_VALIDATOR_CMD"),
        )