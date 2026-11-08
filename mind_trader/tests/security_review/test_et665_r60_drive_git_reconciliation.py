"""Offline R60 tests; no Drive, network, or broker."""
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

SCRIPT = Path(__file__).resolve().parents[2] / "security" / "et665_r60_drive_git_reconciliation.py"

def write_csv(path, cols, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

def run_case(tmp_path, drive_rows, git_rows, mapping=None):
    d, g, o = tmp_path / "drive.csv", tmp_path / "git.csv", tmp_path / "out"
    cols = ["path", "sha256", "size_bytes"]
    write_csv(d, cols, drive_rows)
    write_csv(g, cols, git_rows)
    args = [sys.executable, str(SCRIPT), "--git-manifest", str(g), "--drive-manifest", str(d),
            "--output", str(o), "--expected-git-manifest-sha256", hashlib.sha256(g.read_bytes()).hexdigest(),
            "--expected-drive-manifest-sha256", hashlib.sha256(d.read_bytes()).hexdigest()]
    if mapping:
        m = tmp_path / "mapping.csv"
        write_csv(m, ["drive_path", "git_path"], mapping)
        args.extend(["--mapping", str(m)])
    p = subprocess.run(args, capture_output=True, text=True, timeout=15)
    return p, json.loads((o / "SUMMARY.json").read_text()) if o.exists() else None

def row(path, sha="a"*64, size="10"):
    return {"path": path, "sha256": sha, "size_bytes": size}

def test_match(tmp_path):
    p, summary = run_case(tmp_path, [row("a")], [row("a")])
    assert p.returncode == 0 and summary["counts"]["MATCH"] == 1
    assert summary["full_drive_authority_certified"] is False

def test_mismatch_fail_closed(tmp_path):
    p, summary = run_case(tmp_path, [row("a")], [row("a", "b"*64)])
    assert p.returncode == 2 and summary["counts"]["CONTENT_MISMATCH"] == 1

def test_unmapped_paths_fail_closed(tmp_path):
    p, summary = run_case(tmp_path, [row("drive/a")], [row("git/a")])
    assert p.returncode == 2 and summary["counts"]["DRIVE_ONLY"] == 1 and summary["counts"]["GIT_ONLY"] == 1

def test_explicit_mapping(tmp_path):
    p, summary = run_case(tmp_path, [row("drive/a")], [row("git/a")], [{"drive_path": "drive/a", "git_path": "git/a"}])
    assert p.returncode == 0 and summary["mapping_entries"] == 1

def test_duplicate_drive_path_rejected(tmp_path):
    p, summary = run_case(tmp_path, [row("a"), row("a")], [row("a")])
    assert p.returncode != 0 and summary is None
