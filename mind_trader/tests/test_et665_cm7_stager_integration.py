"""ET665.CM7: behavioral checks for P15 staging, no external services."""
import importlib.util
import json
from pathlib import Path
import pytest

MODULE = Path(__file__).resolve().parents[1] / "security/et665_cm6_evidence_stager.py"
spec = importlib.util.spec_from_file_location("et665_cm7_stager", MODULE)
stager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stager)

def test_engine_stages_manifest_under_temp(tmp_path, monkeypatch):
    monkeypatch.setenv("TEMP", str(tmp_path))
    source = tmp_path / "reports"
    source.mkdir()
    (source / "report.json").write_text('{"real_orders":"FORBIDDEN"}')
    manifest = stager.stage_engine_report(source, "p1516")
    assert manifest.parent.parent == tmp_path / "et665_cm6_exports"
    assert json.loads(manifest.read_text())["real_orders"] == "FORBIDDEN"
    assert (manifest.parent / "report.json").exists()

@pytest.mark.parametrize("engine_id", ["../p1516", "p1516/x", "P1516", "p14", "p15"])
def test_invalid_engine_id_blocked(tmp_path, monkeypatch, engine_id):
    monkeypatch.setenv("TEMP", str(tmp_path))
    source = tmp_path / "reports"
    source.mkdir()
    (source / "report.json").write_text("{}")
    with pytest.raises(PermissionError):
        stager.stage_engine_report(source, engine_id)

def test_source_symlink_root_blocked(tmp_path, monkeypatch):
    monkeypatch.setenv("TEMP", str(tmp_path))
    source = tmp_path / "real"
    source.mkdir()
    (source / "report.json").write_text("{}")
    alias = tmp_path / "alias"
    try:
        alias.symlink_to(source, target_is_directory=True)
    except OSError:
        pytest.skip("symlink privileges unavailable")
    with pytest.raises(PermissionError):
        stager.stage_evidence(alias, tmp_path / "staged")
