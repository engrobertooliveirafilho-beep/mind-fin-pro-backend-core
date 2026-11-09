"""ET665.R381: offline adversarial tests; never launch a subprocess."""
import importlib
import subprocess
from types import SimpleNamespace
from unittest.mock import patch

import pytest


def _module():
    return importlib.import_module("mind_trader.app.audits.institutional_healthcheck")


def test_rejects_unapproved_test_target_without_process():
    mod = _module()
    with patch.object(mod.subprocess, "run") as run:
        with pytest.raises(PermissionError, match="NOT_ALLOWLISTED"):
            mod.run_pytest_suite("../../other")
        run.assert_not_called()


def test_timeout_fails_closed_without_process():
    mod = _module()
    with patch.object(mod.subprocess, "run", side_effect=subprocess.TimeoutExpired(["pytest"], 180)) as run:
        result = mod.run_pytest_suite()
    assert result["passed"] is False
    assert result["returncode"] == 124
    assert run.call_args.kwargs["timeout"] == 180
    assert run.call_args.kwargs["env"]["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] == "1"


def test_oserror_fails_closed_without_process():
    mod = _module()
    with patch.object(mod.subprocess, "run", side_effect=OSError("offline")):
        result = mod.run_pytest_suite()
    assert result["passed"] is False
    assert result["returncode"] == 125


def test_nonzero_exit_is_not_approved():
    mod = _module()
    with patch.object(mod.subprocess, "run", return_value=SimpleNamespace(returncode=1, stdout="", stderr="")) as run:
        result = mod.run_pytest_suite()
    assert result["passed"] is False
    assert run.call_args.args[0][1:] == ["-m", "pytest", "mind_trader/tests", "-q"]


def test_zero_exit_is_only_pytest_pass_not_phase_b_certification():
    mod = _module()
    with patch.object(mod.subprocess, "run", return_value=SimpleNamespace(returncode=0, stdout="ok", stderr="")):
        result = mod.run_pytest_suite()
    assert result["passed"] is True
    assert "phase_b" not in result
