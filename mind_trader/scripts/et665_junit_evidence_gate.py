"""ET665: single fail-closed JUnit evidence validator shared by runner and tests."""
import sys
import xml.etree.ElementTree as ET

EXPECTED_MODULES = frozenset({
    "test_et665_r180_p15_dataset_path_guards",
    "test_et665_r182_p15_rclone_allowlist",
    "test_et665_r183_p15_pipeline_rclone_allowlist",
    "test_et665_r184_mt5_status_truth",
    "test_et665_r186_dependency_gates",
    "test_et665_r196_junit_identity_gate",
})


def validate(xml: str) -> bool:
    try:
        root = ET.fromstring(xml)
        if root.tag not in ("testsuite", "testsuites"):
            return False
        suites = [root] if root.tag == "testsuite" else list(root.findall(".//testsuite"))
        if not suites:
            return False
        cases = root.findall(".//testcase")
        counts = []
        for suite in suites:
            counts.append(tuple(int(suite.attrib[key]) for key in ("tests", "failures", "errors", "skipped")))
        if any(value < 0 for count in counts for value in count):
            return False
        tests, failures, errors, skipped = map(sum, zip(*counts))
        if tests != len(cases) or tests < len(EXPECTED_MODULES) or failures or errors or skipped:
            return False
        if any(not c.attrib.get("name") or not c.attrib.get("classname") for c in cases):
            return False
        if any(any(c.find(tag) is not None for tag in ("failure", "error", "skipped")) for c in cases):
            return False
        observed = {part for case in cases for part in case.attrib["classname"].split(".")}
        return EXPECTED_MODULES.issubset(observed)
    except (ET.ParseError, ValueError, TypeError, KeyError, OSError):
        return False


def main() -> int:
    if len(sys.argv) != 2:
        print("BLOCKED: expected exactly one JUnit XML file path", file=sys.stderr)
        return 2
    try:
        with open(sys.argv[1], encoding="utf-8") as stream:
            xml = stream.read()
    except (OSError, UnicodeError) as exc:
        print(f"BLOCKED: cannot read JUnit evidence: {exc}", file=sys.stderr)
        return 1
    if not validate(xml):
        print("BLOCKED: invalid, incomplete or nonpassing JUnit evidence", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
