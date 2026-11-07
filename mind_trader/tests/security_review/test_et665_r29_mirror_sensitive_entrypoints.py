"""ET665 R29 static security regressions. Never import or run target files."""
import ast
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PREFIX = "products/eldora_trader/mind_trader/"
FUNCTION_GUARDS = {
    "app/p121_200x_autonomous_demo_evidence_factory/engine.py": "snapshot",
    "app/p138_platform_connectors/engine.py": "mt5_probe",
    "app/p139_mt5_historical_data_puller/engine.py": "pull",
    "app/p1516_multi_family_combo_backtest_executor/engine.py": "cmd",
    "app/p1525b_cloud_dataset_reconstruction_fix/engine.py": "cmd",
    "app/p153_p155_profit_market_data_pipeline/engine.py": "run_cmd",
    "app/p156_p1510_real_edge_research_runtime/engine.py": "cmd",
    "app/p1621e_real_video_fetch_loop/engine.py": "fetch_metadata",
    "app/p1621f_transcript_download_strategy_extraction/engine.py": "fetch_subtitles",
    "app/p1622_autonomous_daily_research_cron/engine.py": "run_module",
    "reports/P1505_DATA_INGESTION_ENGINE/p1505b_mt5_harvester.py": "run",
    "reports/P76A2_MT5_DEMO_VALIDATION_FIX/p76a2_demo_validation_fix.py": "run",
    "reports/P76A_MT5_CONNECTION_AUDIT/p76a_mt5_connection_audit.py": "run",
    "reports/P76B_MT5_DEMO_ENVIRONMENT_CERTIFICATION/p76b_certify_environment.py": "run",
    "reports/P77B_DEMO_ORDER_CHECK_FILLING_MODE_FIX/p77b_filling_check.py": "check",
    "reports/P79_DEMO_ORDER_AUDIT_POSITION_MONITOR/p79_monitor.py": "run",
}
TOP_LEVEL_GUARDS = (
    "reports/P1804_REAL_MT5_HISTORY_DOWNLOAD_PROBE/p1804_real_mt5_history_download_probe.py",
    "reports/P1805_SYMBOL_DISCOVERY_AND_10Y_NORMALIZATION/p1805_symbol_discovery_10y_normalization.py",
)

def tree_for(suffix):
    raw = subprocess.check_output(
        ["git", "-C", str(ROOT), "show", "HEAD:" + PREFIX + suffix], timeout=15
    ).decode("utf-8-sig")
    return ast.parse(raw, filename=suffix)

def assert_denial(node, expected):
    assert isinstance(node, ast.Raise)
    assert isinstance(node.exc, ast.Call)
    assert isinstance(node.exc.func, ast.Name)
    assert node.exc.func.id == "PermissionError"
    assert len(node.exc.args) == 1
    assert isinstance(node.exc.args[0], ast.Constant)
    assert node.exc.args[0].value == expected

def test_r29_mirrored_functions_deny_before_sensitive_calls():
    for suffix, name in FUNCTION_GUARDS.items():
        tree = tree_for(suffix)
        matches = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name]
        assert len(matches) == 1, suffix
        assert_denial(matches[0].body[0], "ET665_R29_MIRRORED_EXTERNAL_CAPABILITY_FORBIDDEN")

def test_r29_import_time_probes_deny_before_imports():
    for suffix in TOP_LEVEL_GUARDS:
        tree = tree_for(suffix)
        assert_denial(tree.body[0], "ET665_R29_MIRRORED_TOP_LEVEL_MT5_FORBIDDEN")

def test_r29_all_18_guards_present_and_unique():
    assert len(FUNCTION_GUARDS) == 16
    assert len(TOP_LEVEL_GUARDS) == 2
    assert not set(FUNCTION_GUARDS).intersection(TOP_LEVEL_GUARDS)
