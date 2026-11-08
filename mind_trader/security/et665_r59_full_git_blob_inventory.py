"""ET665.R59: complete read-only SHA-256 inventory of every blob in a Git commit.

This inventories Git-tracked blobs of all file types, not only Python files.
It does not execute repository code, access the network, or mutate the source repo.
A full, non-shallow object database is required for the accompanying fsck gate.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def git(root: Path, *args: str, input_bytes: bytes | None = None) -> bytes:
    p = subprocess.run(
        ["git", "-C", str(root), *args],
        input=input_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if p.returncode:
        raise RuntimeError(
            "GIT_COMMAND_FAILED:"
            + " ".join(args)
            + ":"
            + p.stderr.decode("utf-8", "replace")[-2000:]
        )
    return p.stdout


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--expected-head", default="")
    args = ap.parse_args()

    root = args.repo.resolve(strict=True)
    out = args.output.resolve()
    if not root.is_dir() or not (root / ".git").exists():
        raise SystemExit("REPOSITORY_ROOT_INVALID")
    if out.exists():
        raise SystemExit("OUTPUT_ALREADY_EXISTS")
    if out == root or root in out.parents:
        raise SystemExit("OUTPUT_MUST_BE_OUTSIDE_REPOSITORY")

    head = git(root, "rev-parse", "--verify", "HEAD").decode().strip()
    if args.expected_head and head.lower() != args.expected_head.lower():
        raise SystemExit("EXPECTED_HEAD_MISMATCH:" + head)

    shallow = git(root, "rev-parse", "--is-shallow-repository").decode().strip()
    if shallow != "false":
        raise SystemExit("SHALLOW_REPOSITORY_NOT_ACCEPTED")

    tree = git(root, "ls-tree", "-r", "-z", "--full-tree", "HEAD")
    entries = []
    for raw in tree.split(b"\0"):
        if not raw:
            continue
        metadata, raw_path = raw.split(b"\t", 1)
        mode, obj_type, oid = metadata.decode("ascii").split()
        if obj_type == "blob":
            entries.append((mode, oid, raw_path))

    if not entries:
        raise SystemExit("NO_TRACKED_BLOBS")

    # Stream all unique object IDs through one cat-file process.
    unique_oids = sorted({oid for _, oid, _ in entries})
    proc = subprocess.Popen(
        ["git", "-C", str(root), "cat-file", "--batch"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        assert proc.stdin and proc.stdout
        for oid in unique_oids:
            proc.stdin.write((oid + "\n").encode("ascii"))
        proc.stdin.close()
        hashes = {}
        for oid in unique_oids:
            header = proc.stdout.readline().decode("ascii", "replace").strip().split()
            if len(header) != 3 or header[0] != oid or header[1] != "blob":
                raise RuntimeError("GIT_BLOB_HEADER_MISMATCH:" + oid)
            size = int(header[2])
            digest = hashlib.sha256()
            remaining = size
            while remaining:
                chunk = proc.stdout.read(min(1024 * 1024, remaining))
                if not chunk:
                    raise RuntimeError("GIT_BLOB_TRUNCATED:" + oid)
                digest.update(chunk)
                remaining -= len(chunk)
            if proc.stdout.read(1) != b"\n":
                raise RuntimeError("GIT_BLOB_TERMINATOR_MISSING:" + oid)
            hashes[oid] = (size, digest.hexdigest())
        rc = proc.wait(timeout=120)
        if rc:
            raise RuntimeError("GIT_CAT_FILE_FAILED:" + str(rc))
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait()

    out.mkdir(parents=True)
    manifest = out / "GIT_ALL_BLOBS_SHA256.csv"
    with manifest.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["path", "mode", "git_object_id", "size_bytes", "sha256"])
        for mode, oid, raw_path in sorted(entries, key=lambda x: x[2]):
            size, sha = hashes[oid]
            w.writerow([
                raw_path.decode("utf-8", "surrogateescape"),
                mode,
                oid,
                size,
                sha,
            ])

    fsck = subprocess.run(
        ["git", "-C", str(root), "fsck", "--full", "--strict", "--no-reflogs"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    fsck_log = out / "GIT_FSCK_FULL.log"
    fsck_log.write_text(fsck.stdout, encoding="utf-8")

    summary = {
        "schema": "ET665_R59_ALL_TRACKED_GIT_BLOBS_V1",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "head": head,
        "shallow_repository": False,
        "tracked_blob_paths": len(entries),
        "unique_blob_objects": len(unique_oids),
        "duplicate_blob_paths": len(entries) - len(unique_oids),
        "total_tracked_bytes": sum(hashes[oid][0] for _, oid, _ in entries),
        "git_fsck_exit": fsck.returncode,
        "git_object_integrity": "PASS" if fsck.returncode == 0 else "FAIL",
        "manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest(),
        "fsck_log_sha256": hashlib.sha256(fsck_log.read_bytes()).hexdigest(),
        "drive_equivalence": "NOT_CHECKED",
        "mirror_semantic_equivalence": "NOT_CHECKED",
        "phase_b": "OPEN",
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
    }
    summary_path = out / "GIT_ALL_BLOBS_SUMMARY.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 0 if fsck.returncode == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
