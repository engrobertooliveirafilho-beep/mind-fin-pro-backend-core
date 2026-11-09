"""ET665.R47 inventory tests: offline only, no external process or broker execution."""
import ast
import importlib.util
from pathlib import Path

MODULE = Path(__file__).with_name("et665_r47_execution_path_inventory.py")


def load():
    spec = importlib.util.spec_from_file_location("et665_r47_inventory", MODULE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_r47_detects_process_mt5_network_dynamic_and_parse_errors(tmp_path):
    (tmp_path / "sample.py").write_text("import MetaTrader5 as mt5\nimport subprocess\nsubprocess.run(['echo'])\nmt5.order_send({})\nrequests.post('https://invalid.example')\neval('1')\n", encoding="utf-8")
    (tmp_path / "broken.py").write_text("def broken(:\n", encoding="utf-8")
    checked, findings = load().inventory(tmp_path)
    assert checked == 2
    cats = {x["category"] for x in findings}
    assert {"PROCESS_SPAWN", "MT5_TERMINAL", "MT5_IMPORT", "NETWORK", "DYNAMIC_EXEC", "PARSE_ERROR"} <= cats
    assert all(len(x["sha256"]) == 64 for x in findings)


def test_r47_no_runtime_execution_on_inspected_source(tmp_path):
    marker = tmp_path / "must_not_exist"
    (tmp_path / "candidate.py").write_text("import pathlib\npathlib.Path(" + repr(str(marker)) + ").write_text('bad')\n")
    checked, findings = load().inventory(tmp_path)
    assert checked == 1
    assert not marker.exists()


def test_r47_module_parses():
    ast.parse(MODULE.read_text(encoding="utf-8"))
