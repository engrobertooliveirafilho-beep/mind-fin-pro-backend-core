"""ET665.R384: institutional health cannot pass with skipped tests or corrupt ledger."""
from unittest.mock import patch

import pytest

from mind_trader.app.audits import institutional_healthcheck as hc


@pytest.mark.parametrize("run_tests,tests_ok,ledger_ok,expected", [
    (False, True, True, "SYSTEM_HEALTH_FAIL"),
    (True, False, True, "SYSTEM_HEALTH_FAIL"),
    (True, True, False, "SYSTEM_HEALTH_FAIL"),
    (True, True, True, "SYSTEM_HEALTH_OK"),
])
def test_healthcheck_requires_executed_tests_and_valid_ledger(run_tests, tests_ok, ledger_ok, expected):
    with patch.object(hc, "run_pytest_suite", return_value={"passed": tests_ok}), \
         patch.object(hc, "build_runtime_evidence_package", return_value={"production":"BLOCKED", "live":"FORBIDDEN", "edge_claim":"NONE", "package_hash":"a"*64}), \
         patch.object(hc, "verify_ledger", return_value={"valid":ledger_ok}):
        result = hc.institutional_healthcheck(run_tests=run_tests)
    assert result["decision"] == expected
    assert result["production"] == "BLOCKED"
    assert result["live"] == "FORBIDDEN"
