"""ET665.CM6 — offline evidence packaging for reviewed GitHub publication.

No network, git push, credentials, rclone or historical Drive mutation.
Only stages a manifest and copies verified files to an isolated local directory.
"""
import hashlib
import json
import os
import shutil
from pathlib import Path

MAX_FILE_BYTES = 8 * 1024 * 1024
MAX_FILES = 100
ALLOWED_SUFFIXES = {".json", ".xml", ".txt", ".log", ".csv", ".md"}
FORBIDDEN_NAMES = {".env", "id_rsa", "id_ed25519", "credentials.json", "token.json"}

def _inside(child, parent):
    return child != parent and parent in child.parents

def stage_evidence(source, destination):
    source_input = Path(source)
    destination_input = Path(destination)
    if source_input.is_symlink() or destination_input.is_symlink():
        raise PermissionError("ET665_SYMLINK_ROOT_FORBIDDEN")
    source = source_input.resolve(strict=True)
    destination = destination_input.resolve()
    if not source.is_dir():
        raise PermissionError("ET665_SOURCE_MUST_BE_DIRECTORY")
    if not destination.is_absolute() or not _inside(destination, Path(os.environ.get("TEMP", os.environ.get("TMP", "/tmp"))).resolve()):
        raise PermissionError("ET665_DESTINATION_MUST_BE_TEMP_SUBDIRECTORY")
    if _inside(destination, source) or _inside(source, destination) or source == destination:
        raise PermissionError("ET665_SOURCE_DESTINATION_OVERLAP")
    if destination.exists():
        raise FileExistsError("ET665_NO_OVERWRITE")
    if any(parent.is_symlink() for parent in destination_input.parents):
        raise PermissionError("ET665_SYMLINK_DESTINATION_PARENT")
    paths = sorted(source.iterdir(), key=lambda p: p.name)
    if not paths or len(paths) > MAX_FILES:
        raise ValueError("ET665_INVALID_FILE_COUNT")
    manifest = []
    snapshots = {}
    for p in paths:
        if p.is_symlink() or not p.is_file() or p.name.lower() in FORBIDDEN_NAMES or p.suffix.lower() not in ALLOWED_SUFFIXES:
            raise PermissionError("ET665_UNAPPROVED_FILE")
        if p.stat().st_size > MAX_FILE_BYTES:
            raise ValueError("ET665_FILE_TOO_LARGE")
        data = p.read_bytes()
        if b"-----BEGIN PRIVATE KEY-----" in data or b"ghp_" in data or b"github_pat_" in data:
            raise PermissionError("ET665_SECRET_MARKER_DETECTED")
        snapshots[p.name] = data
        manifest.append({"file": p.name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    destination.mkdir(parents=True, exist_ok=False)
    try:
        for item in manifest:
            dst = destination / item["file"]
            with dst.open("xb") as writer:
                writer.write(snapshots[item["file"]])
            if hashlib.sha256(dst.read_bytes()).hexdigest() != item["sha256"]:
                raise IOError("ET665_STAGING_HASH_MISMATCH")
        (destination / "manifest.sha256.json").write_text(
            json.dumps({"status": "STAGED_FOR_REVIEW_NOT_PUBLISHED", "files": manifest,
                        "real_orders": "FORBIDDEN", "ftmo_real": "FORBIDDEN"},
                       indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except BaseException:
        shutil.rmtree(destination)
        raise
    return destination / "manifest.sha256.json"


def stage_engine_report(source, engine_id):
    """Stage one P15 report locally; no GitHub/Drive publication."""
    import re
    import uuid
    if not re.fullmatch(r"p15[a-z0-9_]{1,48}", engine_id):
        raise PermissionError("ET665_INVALID_ENGINE_ID")
    temp_root = Path(os.environ.get("TEMP", os.environ.get("TMP", "/tmp"))).resolve()
    destination = temp_root / "et665_cm6_exports" / (engine_id + "_" + uuid.uuid4().hex)
    return stage_evidence(source, destination)
