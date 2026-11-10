import subprocess,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from mind_trader.experimental import et665_r389_offline_regression_runner as m
class R389(unittest.TestCase):
    def test_six_regression_modules(self):
        self.assertEqual(len(m.MODULES),6)
        self.assertEqual(len(set(m.MODULES)),6)
    def test_failure_creates_evidence(self):
        class Failed:
            returncode=1
            stdout=""
            stderr="FAILED (failures=1)"
        with tempfile.TemporaryDirectory() as d,patch.object(m.subprocess,"run",return_value=Failed()):
            r=m.run(d)
            self.assertEqual(r["status"],"FAIL_CLOSED")
            self.assertEqual(r["phase_b_certified"],0)
            self.assertTrue((Path(d)/"r389_tests.log").exists())
            self.assertTrue((Path(d)/"r389_evidence.json").exists())
    def test_false_success_log_rejected(self):
        class Fake:
            returncode=0
            stdout="not actually tested"
            stderr=""
        with tempfile.TemporaryDirectory() as d,patch.object(m.subprocess,"run",return_value=Fake()):
            self.assertEqual(m.run(d)["status"],"FAIL_CLOSED")
    def test_valid_unittest_log_accepted(self):
        class Passed:
            returncode=0
            stdout=""
            stderr="Ran 19 tests in 0.417s\n\nOK\n"
        with tempfile.TemporaryDirectory() as d,patch.object(m.subprocess,"run",return_value=Passed()):
            r=m.run(d)
            self.assertEqual(r["status"],"PASS")
    def test_zero_tests_not_accepted(self):
        class Empty:
            returncode=0
            stdout=""
            stderr="Ran 0 tests in 0.001s\n\nOK\n"
        with tempfile.TemporaryDirectory() as d,patch.object(m.subprocess,"run",return_value=Empty()):
            self.assertEqual(m.run(d)["status"],"FAIL_CLOSED")
    def test_timeout_retains_fail_closed_evidence(self):
        with tempfile.TemporaryDirectory() as d,patch.object(m.subprocess,"run",
                side_effect=subprocess.TimeoutExpired(cmd=["python"],timeout=120)):
            r=m.run(d)
            self.assertEqual(r["exit_code"],124)
            self.assertEqual(r["status"],"FAIL_CLOSED")
            self.assertTrue((Path(d)/"r389_evidence.json").exists())
    def test_missing_runtime_retains_fail_closed_evidence(self):
        with tempfile.TemporaryDirectory() as d,patch.object(m.subprocess,"run",
                side_effect=FileNotFoundError("python unavailable")):
            r=m.run(d)
            self.assertEqual(r["exit_code"],127)
            self.assertEqual(r["status"],"FAIL_CLOSED")
            self.assertTrue((Path(d)/"r389_tests.log").exists())
    def test_too_few_tests_rejected(self):
        class Incomplete:
            returncode=0
            stdout=""
            stderr="Ran 1 test in 0.001s\n\nOK\n"
        with tempfile.TemporaryDirectory() as d,patch.object(m.subprocess,"run",return_value=Incomplete()):
            self.assertEqual(m.run(d)["status"],"FAIL_CLOSED")
    def test_skipped_tests_rejected(self):
        class Skipped:
            returncode=0
            stdout=""
            stderr="Ran 19 tests in 0.001s\n\nOK (skipped=1)\n"
        with tempfile.TemporaryDirectory() as d,patch.object(m.subprocess,"run",return_value=Skipped()):
            self.assertEqual(m.run(d)["status"],"FAIL_CLOSED")
    def test_real_orders_forbidden(self):
        class Passed:
            returncode=0
            stdout="Ran 19 tests in 0.001s\n\nOK"
            stderr=""
        with tempfile.TemporaryDirectory() as d,patch.object(m.subprocess,"run",return_value=Passed()):
            r=m.run(d)
            self.assertEqual(r["real_orders"],"FORBIDDEN")
            self.assertEqual(r["official_hp19_certified"],0)
if __name__=="__main__":unittest.main()
