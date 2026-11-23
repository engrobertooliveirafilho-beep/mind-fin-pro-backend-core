"""Targeted regression: validate the original loader without legacy top-level writes."""
import ast
import json
from pathlib import Path
import pytest

SOURCE = Path(__file__).resolve().parents[1] / "mind_trader/reports/P1721_TO_P1735_MARKET_INTELLIGENCE_FUSION/p1721_to_p1735_fusion_stack.py"


def _load_function():
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "load")
    namespace = {"json": json}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), str(SOURCE), "exec"), namespace)
    return namespace["load"]


def test_missing_source_fails_closed(tmp_path):
    with pytest.raises(FileNotFoundError):
        _load_function()(tmp_path / "absent.json")


def test_corrupt_source_fails_closed(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text("{bad", encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        _load_function()(p)


def test_wrong_schema_fails_closed(tmp_path):
    p = tmp_path / "dict.json"
    p.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="INVALID_FUSION_INPUT_SCHEMA"):
        _load_function()(p)


def test_valid_list_loads(tmp_path):
    p = tmp_path / "valid.json"
    p.write_text('[{"asset":"XAUUSD"}]', encoding="utf-8")
    assert _load_function()(p) == [{"asset": "XAUUSD"}]
