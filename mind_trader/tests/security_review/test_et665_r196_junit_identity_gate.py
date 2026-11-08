"""ET665 R196: local, offline JUnit module-identity regression fixtures."""
import unittest
import xml.etree.ElementTree as ET

MODULES = (
    "test_et665_r180_p15_dataset_path_guards",
    "test_et665_r182_p15_rclone_allowlist",
    "test_et665_r183_p15_pipeline_rclone_allowlist",
    "test_et665_r184_mt5_status_truth",
    "test_et665_r186_dependency_gates",
    "test_et665_r196_junit_identity_gate",
)

# Load the exact validator executed by the offline runner; no duplicated logic.
import importlib.util
from pathlib import Path

_GATE = Path(__file__).resolve().parents[2] / "scripts" / "et665_junit_evidence_gate.py"
_SPEC = importlib.util.spec_from_file_location("et665_junit_evidence_gate", _GATE)
_GATE_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_GATE_MODULE)
validate = _GATE_MODULE.validate

def report(names=MODULES, **attrs):
    suite = ET.Element("testsuite", {"tests": str(len(names)), "failures": "0", "errors": "0", "skipped": "0", **attrs})
    for n in names:
        ET.SubElement(suite, "testcase", {"classname": "mind_trader.tests.security_review." + n, "name": "test_safety"})
    return ET.tostring(suite, encoding="unicode")

class GateTests(unittest.TestCase):
    def test_valid(self): self.assertTrue(validate(report()))
    def test_missing_module(self): self.assertFalse(validate(report(MODULES[:-1])))
    def test_name_spoof(self): self.assertFalse(validate(report(["unrelated"] * len(MODULES)).replace("test_safety", "test_r180_r182_r183_r184_r186_r196")))
    def test_substring_spoof(self): self.assertFalse(validate(report(["fake_" + m for m in MODULES])))
    def test_pytest_unittest_classname(self):
        xml = report().replace('name="test_safety"', 'name="test_safety"').replace('" name="test_safety"', '.GateTests" name="test_safety"')
        self.assertTrue(validate(xml))
    def test_skipped(self): self.assertFalse(validate(report(skipped="1")))
    def test_count_mismatch(self): self.assertFalse(validate(report(tests="99")))
    def test_invalid_xml(self):
        self.assertFalse(validate("<testsuite>"))
    def test_case_failure(self):
        self.assertFalse(validate(report().replace('name="test_safety" />', 'name="test_safety"><failure /></testcase>', 1)))

if __name__ == "__main__":
    unittest.main()
