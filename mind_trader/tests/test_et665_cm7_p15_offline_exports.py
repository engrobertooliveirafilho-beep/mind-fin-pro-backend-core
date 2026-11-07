"""ET665.CM7: structural regressions for four P15 engines, offline only."""
import ast
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
ENGINES = {
    "app/p1516_multi_family_combo_backtest_executor/engine.py": "p1516",
    "app/p1525b_cloud_dataset_reconstruction_fix/engine.py": "p1525b",
    "app/p153_p155_profit_market_data_pipeline/engine.py": "p153_p155",
    "app/p156_p1510_real_edge_research_runtime/engine.py": "p156_p1510",
}

@pytest.mark.parametrize("path,engine_id", ENGINES.items())
def test_report_staging_replaces_remote_upload(path, engine_id):
    tree = ast.parse((ROOT / path).read_text(encoding="utf-8"))
    run = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "run")
    calls = [n for n in ast.walk(run) if isinstance(n, ast.Call)]
    staged = [n for n in calls if isinstance(n.func, ast.Name) and n.func.id == "stage_engine_report"]
    assert len(staged) == 1
    assert len(staged[0].args) == 2
    assert isinstance(staged[0].args[1], ast.Constant) and staged[0].args[1].value == engine_id
    for call in calls:
        if isinstance(call.func, ast.Name) and call.func.id in {"cmd", "run_cmd"}:
            assert not any(
                isinstance(a, ast.JoinedStr) and any(
                    isinstance(v, ast.FormattedValue) and isinstance(v.value, ast.Name)
                    and v.value.id in {"REMOTE_REPORTS", "REMOTE_NORM"}
                    for v in a.values
                ) for a in call.args
            )

@pytest.mark.parametrize("path", ENGINES)
def test_existing_read_only_rclone_guard_remains(path):
    tree = ast.parse((ROOT / path).read_text(encoding="utf-8"))
    funcs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    guard = funcs.get("cmd") or funcs.get("run_cmd")
    assert guard is not None
    assert "ET665_DRIVE_HISTORICAL_WRITE_FORBIDDEN" in ast.unparse(guard)
    assert "shell=False" in ast.unparse(guard)
    assert "check=True" in ast.unparse(guard)
