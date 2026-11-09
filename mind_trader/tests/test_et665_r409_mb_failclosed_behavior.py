"""R409: behavioral fail-closed regressions; no actual subprocess is started."""
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

RUNNERS = (
    "et665_mb_phase_b_runner.py",
    "et665_mb_r8_consolidated_runner.py",
)

@pytest.mark.parametrize("runner", RUNNERS)
@pytest.mark.parametrize(
    ("failure", "expected"),
    (
        (OSError("simulated process failure"), 126),
        (subprocess.TimeoutExpired("pytest", 180), 124),
    ),
    ids=("oserror", "timeout"),
)
def test_mb_runner_fail_closed_without_launching_process(runner, failure, expected, tmp_path):
    path = Path(__file__).resolve().parents[1] / "security" / runner
    spec = importlib.util.spec_from_file_location("et665_r409_" + runner[:-3], path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    output = tmp_path / "evidence"
    with patch.object(sys, "argv", [str(path), "--output", str(output)]), \
         patch.dict(os.environ, {"TEMP": str(tmp_path), "TMP": str(tmp_path)}), \
         patch.object(module.subprocess, "run", side_effect=failure) as mocked:
        rc = module.main()
    mocked.assert_called_once()
    decision = json.loads((output / "decision.json").read_text(encoding="utf-8"))
    assert rc != 0
    assert decision["pytest_exit_code"] == expected
    assert decision["test_counts"]["tests"] == 0
    assert decision["gates"]["focused_regressions"] == "BLOCKED"
    assert decision["phase_b"] == "BLOCKED"
    assert decision["real_orders"] == "FORBIDDEN"
    assert decision["ftmo_real"] == "FORBIDDEN"
    assert (tmp_path / "evidence.zip").is_file()
