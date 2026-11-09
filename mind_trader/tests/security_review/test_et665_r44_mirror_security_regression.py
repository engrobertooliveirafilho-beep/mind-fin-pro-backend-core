"""ET665.R44: offline, non-executing mirror security invariants."""
import ast
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FILES = (
    "app/security/institutional_live_lock.py",
    "app/execution/safe_broker_adapter.py",
    "app/execution/paper_fill_model.py",
    "app/execution/paper_session.py",
)


def git_source(path):
    return subprocess.check_output(
        ["git", "-C", str(ROOT), "show", "HEAD:" + path], timeout=20
    ).decode("utf-8-sig")


def test_r44_mirrors_equal_and_parse():
    for suffix in FILES:
        path = "mind_trader/" + suffix
        primary = git_source(path)
        mirror = git_source("products/eldora_trader/" + path)
        assert mirror == primary, path
        ast.parse(primary, filename=path)
        ast.parse(mirror, filename="products/eldora_trader/" + path)


def test_r44_live_lock_rejects_unknown_and_redacts_payload():
    source = git_source("products/eldora_trader/mind_trader/app/security/institutional_live_lock.py")
    assert "blocked = not known_research" in source
    assert '"payload_redacted": True' in source
    assert '"PAPER", "REPLAY", "MICRO_SIM"' in source
    assert '"payload": payload' not in source


def test_r44_paper_validations_fail_closed():
    fill = git_source("products/eldora_trader/mind_trader/app/execution/paper_fill_model.py")
    session = git_source("products/eldora_trader/mind_trader/app/execution/paper_session.py")
    adapter = git_source("products/eldora_trader/mind_trader/app/execution/safe_broker_adapter.py")
    assert "math.isfinite" in fill
    assert "math.isfinite" in session
    assert "BLOCK_CORRUPT_PAPER_SESSION" in session
    assert "not isinstance(order, dict)" in adapter
    assert "FORCE_BLOCK_BROKER_SEND_ORDER" in adapter
