from __future__ import annotations

import json
from pathlib import Path

from app.eldora_media_runtime.config import Settings
from app.eldora_media_runtime.pipeline import EldoraMediaPipeline


def _settings(tmp_path: Path) -> Settings:
    canon = tmp_path / "canon"
    canon.mkdir()
    # Arquivo mínimo para teste de descoberta; o runtime não interpreta pixels nesta unidade.
    (canon / "MASTER_CANON_15_001.jpg").write_bytes(b"fake-image")
    return Settings(
        repo_root=tmp_path,
        runtime_root=tmp_path / "runtime",
        canon_root=canon,
        output_root=tmp_path / "output",
        evidence_root=tmp_path / "evidence",
        image_generator_cmd=None,
        video_generator_cmd=None,
        identity_validator_cmd=None,
    )


def test_audit_finds_canon(tmp_path: Path) -> None:
    report = EldoraMediaPipeline(_settings(tmp_path)).audit()
    assert report["canon_status"] == "PASS"
    assert report["canon_assets"] == 1


def test_plan_creates_manifest(tmp_path: Path) -> None:
    batch = EldoraMediaPipeline(_settings(tmp_path)).plan(count=2)
    manifest = json.loads((batch / "batch_manifest.json").read_text(encoding="utf-8"))
    assert manifest["schema"] == "eldora.media.batch.v1"
    assert len(manifest["items"]) == 2
    assert len(list((batch / "01_PROMPTS_READY").glob("*.json"))) == 2