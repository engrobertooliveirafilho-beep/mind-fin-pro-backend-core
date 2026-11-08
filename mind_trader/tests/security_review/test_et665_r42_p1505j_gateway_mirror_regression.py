"""ET665.R42: offline static regressions; never import execution modules."""
import ast
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MIRROR = "products/eldora_trader/"


def tracked_source(path):
    return subprocess.check_output(
        ["git", "-C", str(ROOT), "show", "HEAD:" + path], timeout=20
    ).decode("utf-8-sig")


def test_p1505j_both_copies_parse_and_match():
    path = "mind_trader/reports/P1505_DATA_INGESTION_ENGINE/p1505j_merge_diversified_mt5.py"
    primary = tracked_source(path)
    mirrored = tracked_source(MIRROR + path)
    assert primary == mirrored
    ast.parse(primary, filename=path)
    ast.parse(mirrored, filename=MIRROR + path)


def test_gateway_mirror_matches_canonical_fail_closed():
    path = "mind_trader/app/execution/gateway.py"
    primary = tracked_source(path)
    mirrored = tracked_source(MIRROR + path)
    assert mirrored == primary
    tree = ast.parse(mirrored, filename=MIRROR + path)
    assert any(isinstance(node, ast.FunctionDef) and node.name == "submit_order"
               for node in ast.walk(tree))
    assert "BLOCKED_INVALID_ORDER_INPUT_TYPE" in mirrored
    assert "BLOCKED_MISSING_ORDER_FIELDS" in mirrored
    assert 'paper_broker["fill"].get("filled") is not True' in mirrored
    assert 'ALLOWED_MODES={"PAPER","REPLAY","MICRO_SIM"}' in mirrored
