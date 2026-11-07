"""ET665.CM6 offline stager regressions. No external services."""
import hashlib
import importlib.util
import json
from pathlib import Path
from unittest.mock import patch
import pytest

MODULE = Path(__file__).resolve().parents[1] / "security/et665_cm6_evidence_stager.py"
spec = importlib.util.spec_from_file_location("et665_cm6_stager", MODULE)
stager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stager)

def test_stages_and_hashes_without_network(tmp_path, monkeypatch):
    monkeypatch.setenv("TEMP", str(tmp_path))
    src = tmp_path / "source"
    src.mkdir()
    (src / "junit.xml").write_text("<testsuite tests='1'/>", encoding="utf-8")
    with patch.object(stager.shutil, "copyfileobj", wraps=stager.shutil.copyfileobj):
        manifest = stager.stage_evidence(src, tmp_path / "staged")
    data = json.loads(manifest.read_text())
    assert data["status"] == "STAGED_FOR_REVIEW_NOT_PUBLISHED"
    assert data["files"][0]["sha256"] == hashlib.sha256((src / "junit.xml").read_bytes()).hexdigest()
    assert (tmp_path / "staged" / "junit.xml").read_bytes() == (src / "junit.xml").read_bytes()

def test_refuses_drive_like_external_destination(tmp_path, monkeypatch):
    monkeypatch.setenv("TEMP", str(tmp_path / "temp"))
    src = tmp_path / "src"
    src.mkdir()
    (src / "test.txt").write_text("safe")
    with pytest.raises(PermissionError):
        stager.stage_evidence(src, tmp_path / "outside")

def test_refuses_overwrite(tmp_path, monkeypatch):
    monkeypatch.setenv("TEMP", str(tmp_path))
    src = tmp_path / "src"
    src.mkdir()
    (src / "test.txt").write_text("safe")
    dst = tmp_path / "dst"
    dst.mkdir()
    with pytest.raises(FileExistsError):
        stager.stage_evidence(src, dst)

@pytest.mark.parametrize("filename,body", [
    (".env", "PASSWORD=secret"),
    ("credentials.json", "{}"),
    ("safe.txt", "-----BEGIN PRIVATE KEY-----"),
    ("safe.txt", "github_pat_test"),
])
def test_refuses_secrets(tmp_path, monkeypatch, filename, body):
    monkeypatch.setenv("TEMP", str(tmp_path))
    src = tmp_path / "src"
    src.mkdir()
    (src / filename).write_text(body)
    with pytest.raises(PermissionError):
        stager.stage_evidence(src, tmp_path / "staged")
    assert not (tmp_path / "staged").exists()

def test_refuses_symlink(tmp_path, monkeypatch):
    monkeypatch.setenv("TEMP", str(tmp_path))
    src = tmp_path / "src"
    src.mkdir()
    target = tmp_path / "secret.txt"
    target.write_text("data")
    try:
        (src / "alias.txt").symlink_to(target)
    except OSError:
        pytest.skip("symlink privileges unavailable")
    with pytest.raises(PermissionError):
        stager.stage_evidence(src, tmp_path / "staged")
