"""ET665.R182: exact argv allowlist for P15 rclone reads; subprocess is mocked."""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
ENGINES = (
    "app/p1516_multi_family_combo_backtest_executor/engine.py",
    "app/p1525b_cloud_dataset_reconstruction_fix/engine.py",
)


def load_engine(relative, tmp_path):
    spec = importlib.util.spec_from_file_location(
        "et665_r182_" + relative.replace("/", "_").replace(".", "_"),
        ROOT / relative,
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.DATA = tmp_path / "normalized" / "nested path"
    return module


@pytest.mark.parametrize("relative", ENGINES)
def test_only_exact_read_only_rclone_argv_is_allowed(relative, tmp_path, monkeypatch):
    module = load_engine(relative, tmp_path)
    observed = []

    def fake_run(args, **kwargs):
        observed.append((args, kwargs))
        return "MOCKED"

    monkeypatch.setattr(module.subprocess, "run", fake_run)
    command = ["rclone", "copy", module.REMOTE_NORM, str(module.DATA), "--progress"]
    assert module.cmd(command) == "MOCKED"
    assert observed == [(
        command,
        {"shell": False, "capture_output": True, "text": True, "check": True},
    )]


@pytest.mark.parametrize("relative", ENGINES)
@pytest.mark.parametrize("mutation", ("remote_source", "local_destination", "extra_flag", "remote_target"))
def test_mutated_rclone_commands_are_rejected_without_subprocess(relative, mutation, tmp_path, monkeypatch):
    module = load_engine(relative, tmp_path)
    called = []
    monkeypatch.setattr(module.subprocess, "run", lambda *a, **k: called.append((a, k)))
    command = ["rclone", "copy", module.REMOTE_NORM, str(module.DATA), "--progress"]
    if mutation == "remote_source":
        command[2] = "gdrive:other-folder"
    elif mutation == "local_destination":
        command[3] = str(tmp_path / "outside")
    elif mutation == "extra_flag":
        command.append("--delete-excluded")
    elif mutation == "remote_target":
        command[3] = "gdrive:other-target"
    with pytest.raises(PermissionError, match="ET665_RCLONE_COMMAND_NOT_ALLOWLISTED"):
        module.cmd(command)
    assert called == []


@pytest.mark.parametrize("relative", ENGINES)
def test_command_requires_argv_not_shell_string(relative, tmp_path, monkeypatch):
    module = load_engine(relative, tmp_path)
    called = []
    monkeypatch.setattr(module.subprocess, "run", lambda *a, **k: called.append((a, k)))
    with pytest.raises(PermissionError, match="ET665_RCLONE_COMMAND_NOT_ALLOWLISTED"):
        module.cmd('rclone copy "gdrive:source" "C:\\temp\\data" --progress')
    assert called == []
