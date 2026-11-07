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
            # Read-only Drive -> local is allowed; reject any Drive destination.
            for arg in call.args:
                if not isinstance(arg, ast.JoinedStr):
                    continue
                rendered = ast.unparse(arg)
                assert "REMOTE_REPORTS" not in rendered, "Historical report upload forbidden"
                if "REMOTE_NORM" in rendered:
                    assert "REMOTE_NORM" == next(
                        (v.value.id for v in arg.values
                         if isinstance(v, ast.FormattedValue)
                         and isinstance(v.value, ast.Name)
                         and v.value.id.startswith("REMOTE_")), None
                    ), "Remote source must be the first remote path"
                    # A remote destination would require a second remote argument
                    # or a source-local -> remote ordering.
                    remote_positions = [
                        i for i, v in enumerate(arg.values)
                        if isinstance(v, ast.FormattedValue)
                        and isinstance(v.value, ast.Name)
                        and v.value.id.startswith("REMOTE_")
                    ]
                    assert remote_positions == [1], "Only remote-to-local copy permitted"

@pytest.mark.parametrize("path", ENGINES)
def test_existing_read_only_rclone_guard_remains(path):
    tree = ast.parse((ROOT / path).read_text(encoding="utf-8"))
    funcs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    guard = funcs.get("cmd") or funcs.get("run_cmd")
    assert guard is not None
    assert "ET665_DRIVE_HISTORICAL_WRITE_FORBIDDEN" in ast.unparse(guard)
    assert "shell=False" in ast.unparse(guard)
    assert "check=True" in ast.unparse(guard)
