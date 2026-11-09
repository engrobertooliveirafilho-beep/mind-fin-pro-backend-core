"""ET665.R383: both offline runners fail closed on subprocess failures, with mocked execution."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[3]
RUNNERS = [
    "mind_trader/security/et665_mb_phase_b_runner.py",
    "mind_trader/security/et665_mb_r8_consolidated_runner.py",
]


def _load(path):
    spec = importlib.util.spec_from_file_location("et665_r383_runner", ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("path", RUNNERS)
@pytest.mark.parametrize("failure,expected_code", [
    (OSError("executable unavailable"), 126),
    (subprocess.TimeoutExpired(["python", "-m", "pytest"], 180), 124),
])
def test_runner_subprocess_failure_blocks_and_writes_evidence(path, failure, expected_code, tmp_path, monkeypatch):
    runner = _load(path)
    out = tmp_path / "evidence"
    monkeypatch.setenv("TEMP", str(tmp_path))
    monkeypatch.setenv("TMP", str(tmp_path))
    monkeypatch.setattr(sys, "argv", [path, "--output", str(out)])
    with patch.object(runner.subprocess, "run", side_effect=failure) as mocked:
        exit_code = runner.main()
    assert exit_code != 0
    mocked.assert_called_once()
    assert mocked.call_args.kwargs["timeout"] == 180
    assert mocked.call_args.kwargs["cwd"] == runner.ROOT
    evidence = json.loads((out / "decision.json").read_text(encoding="utf-8"))
    assert evidence["pytest_exit_code"] == expected_code
    assert evidence["phase_b"] == "BLOCKED"
    assert evidence["real_orders"] == "FORBIDDEN"
    assert evidence["ftmo_real"] == "FORBIDDEN"
    assert evidence["gates"]["focused_regressions"] == "BLOCKED"
    assert (out / "execution.log").is_file()
    assert (tmp_path / "evidence.zip").is_file()
