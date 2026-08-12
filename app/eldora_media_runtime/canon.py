from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

SUPPORTED_IMAGES = {".jpg", ".jpeg", ".png", ".webp"}


@dataclass(frozen=True)
class CanonAsset:
    path: Path
    sha256: str
    bytes: int


class CanonError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def discover_canon_assets(canon_root: Path) -> list[CanonAsset]:
    if not canon_root.exists():
        raise CanonError(f"Canon root ausente: {canon_root}")

    assets = [
        CanonAsset(path=p, sha256=sha256_file(p), bytes=p.stat().st_size)
        for p in canon_root.rglob("*")
        if p.is_file() and p.suffix.lower() in SUPPORTED_IMAGES
    ]

    if not assets:
        raise CanonError(
            "Nenhuma referência visual encontrada. Sincronize MASTER_CANON_15/BEST_OF_BEST_V1 antes de produzir."
        )

    return sorted(assets, key=lambda item: str(item.path).lower())