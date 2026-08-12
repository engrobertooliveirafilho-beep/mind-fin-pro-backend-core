from pathlib import Path
from mind_trader.app.audits.institutional_healthcheck import assert_critical_blocks, institutional_healthcheck, save_healthcheck_report

def test_assert_critical_blocks_passes():
    p={"production":"BLOCKED","live":"FORBIDDEN","edge_claim":"NONE","package_hash":"a"*64}
    r=assert_critical_blocks(p)
    assert r["passed"] is True

def test_assert_critical_blocks_fails_on_live():
    p={"production":"BLOCKED","live":"LIVE","edge_claim":"NONE","package_hash":"a"*64}
    r=assert_critical_blocks(p)
    assert r["passed"] is False

def test_institutional_healthcheck_no_tests():
    r=institutional_healthcheck(run_tests=False,expected_tests=141)
    assert r["decision"]=="SYSTEM_HEALTH_OK"
    assert r["production"]=="BLOCKED"
    assert r["live"]=="FORBIDDEN"

def test_save_healthcheck_report(tmp_path):
    r=save_healthcheck_report(str(tmp_path/"health.json"),False,141)
    assert Path(tmp_path/"health.json").exists()
    assert r["edge_claim"]=="NONE"
