"""ET665.R183: strict rclone argv contracts for P15.3-5 and P15.6-10."""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
ENGINES = (
    ("app/p153_p155_profit_market_data_pipeline/engine.py", "run_cmd", "REMOTE_RAW", "RAW"),
    ("app/p156_p1510_real_edge_research_runtime/engine.py", "cmd", "REMOTE_NORM", "DATA"),
)


def load_engine(relative, tmp_path):
    spec = importlib.util.spec_from_file_location(
        "et665_r183_" + relative.replace("/", "_").replace(".", "_"),
        ROOT / relative,
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("relative,method,remote_name,local_name", ENGINES)
def test_only_exact_remote_to_local_copy_is_allowed(relative, method, remote_name, local_name, tmp_path, monkeypatch):
    module = load_engine(relative, tmp_path)
    local = tmp_path / "windows-like path" / "data"
    setattr(module, local_name, local)
    expected = ["rclone", "copy", getattr(module, remote_name), str(local), "--progress"]
    called = []
    monkeypatch.setattr(module.subprocess, "run", lambda args, **kwargs: called.append((args, kwargs)) or "MOCKED")
    assert getattr(module, method)(expected) == "MOCKED"
    assert called == [(expected, {"shell": False, "capture_output": True, "text": True, "check": True})]


@pytest.mark.parametrize("relative,method,remote_name,local_name", ENGINES)
@pytest.mark.parametrize("mutation", ("remote_source", "local_destination", "extra_flag", "remote_target"))
def test_rejects_mutated_copy_commands_before_subprocess(relative, method, remote_name, local_name, mutation, tmp_path, monkeypatch):
    module = load_engine(relative, tmp_path)
    local = tmp_path / "normalized"
    setattr(module, local_name, local)
    command = ["rclone", "copy", getattr(module, remote_name), str(local), "--progress"]
    if mutation == "remote_source":
        command[2] = "gdrive:unapproved"
    elif mutation == "local_destination":
        command[3] = str(tmp_path / "outside")
    elif mutation == "extra_flag":
        command.append("--delete-excluded")
    else:
        command[3] = "gdrive:other-target"
    called = []
    monkeypatch.setattr(module.subprocess, "run", lambda *args, **kwargs: called.append((args, kwargs)))
    with pytest.raises(PermissionError, match="ET665_RCLONE_COMMAND_NOT_ALLOWLISTED"):
        getattr(module, method)(command)
    assert called == []


@pytest.mark.parametrize("relative,method,remote_name,local_name", ENGINES)
def test_rejects_shell_string_without_invoking_subprocess(relative, method, remote_name, local_name, tmp_path, monkeypatch):
    module = load_engine(relative, tmp_path)
    called = []
    monkeypatch.setattr(module.subprocess, "run", lambda *args, **kwargs: called.append((args, kwargs)))
    with pytest.raises(PermissionError, match="ET665_RCLONE_COMMAND_NOT_ALLOWLISTED"):
        getattr(module, method)('rclone copy "gdrive:source" "C:\\temp\\data" --progress')
    assert called == []
