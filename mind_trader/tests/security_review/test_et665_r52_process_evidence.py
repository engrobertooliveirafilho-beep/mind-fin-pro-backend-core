"""R52 must not convert static review into permission to execute."""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
spec = importlib.util.spec_from_file_location("r52", HERE / "et665_r52_process_evidence.py")
r52 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r52)


def test_r52_classification_preserves_pending_status():
    cases = [
        ("app/p1516_multi_family_combo_backtest_executor/engine.py", "P15_DRIVE_READ_TO_LOCAL"),
        ("app/audits/institutional_healthcheck.py", "PYTEST_HEALTHCHECK"),
        ("security/et665_r23_full_tree_inventory.py", "GIT_READ_ONLY_AUDIT"),
        ("tests/security_review/test_et665_r44_mirror_security_regression.py", "TEST_GIT_SUBPROCESS"),
    ]
    for path, expected in cases:
        purpose, status, reason = r52.classify({"path": path})
        assert purpose == expected
        assert "CERTIFIED" not in status or status.endswith("NOT_CERTIFIED")
        assert reason


def test_r52_report_is_fail_closed(tmp_path):
    root = tmp_path / "src"
    root.mkdir()
    (root / "unknown.py").write_text("import subprocess\nsubprocess.run(['echo'])\n", encoding="utf-8")
    result = r52.report(root, tmp_path / "out")
    assert result["findings_total"] == 1
    assert result["unclassified"] == 1
    assert result["authorized_execution"] == 0
    assert result["security_certification"] == "NOT_GRANTED"
    assert result["real_orders"] == "FORBIDDEN"
