import os

from app.runtime.authority_shadow_ledger import build_shadow_authority_ledger


def test_p495h2_shadow_ledger_builds():
    os.environ["MIND_ENABLE_MINDOS_ASSISTED_BYPASS"] = "1"

    ledger = build_shadow_authority_ledger("u1", "marketing para vender consultoria")

    assert ledger["ok"] is True
    assert ledger["mode"] == "SHADOW_ONLY"
    assert len(ledger["candidates"]) >= 1
    assert ledger["selection"]["ok"] is True
    assert ledger["selection"]["send_to_user"] is False
