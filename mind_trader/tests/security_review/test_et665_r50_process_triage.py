"""ET665.R50 triage is read-only and never auto-approves execution."""
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("et665_r50_process_triage", HERE / "et665_r50_process_triage.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_r50_no_automatic_approval(tmp_path):
    root = tmp_path / "src"
    root.mkdir()
    (root / "sample.py").write_text("import subprocess\nsubprocess.run(['echo','x'])\neval('1+1')\n", encoding="utf-8")
    result = module.triage(root, tmp_path / "out")
    assert result["approved_for_execution"] == 0
    assert result["certification"] == "NOT_GRANTED"
    assert result["phase_b"] == "OPEN"
    assert result["findings_total"] == 2
    assert (tmp_path / "out" / "R50_TRIAGE.csv").exists()


def test_r50_classification_fails_closed():
    for category in ("PROCESS_SPAWN", "DYNAMIC_EXEC", "MT5_IMPORT", "MT5_TERMINAL"):
        priority, disposition, reason = module.classify({"category": category})
        assert priority in ("HIGH", "CRITICAL")
        assert disposition != "APPROVED"
        assert reason
