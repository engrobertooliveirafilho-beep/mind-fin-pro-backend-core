"""Offline, read-only verifier for ET665 R19 evidence ZIP; no network or broker calls."""
import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

EXPECTED_ZIP_SHA = "8ad07238d895793fcb0b109c7620813efebe4b69f66c99eec05eee4f87901d6c"
EXPECTED_LOG_SHA = "987429792b0331623b373a8a8fdad534319f09690bce11231ef99b759f8d00a2"
EXPECTED_JUNIT_SHA = "e8b7e59bee426166a3ac7434cd863103ac7ae40cd9c1c31a190bc4ecbc8d314c"
EXPECTED_CASES = 264
REQUIRED_ENGINES = ("p1516", "p1525b", "p153_p155", "p156_p1510")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def verify(path):
    findings = []
    zip_sha = digest(path.read_bytes())
    findings.append(("ZIP_SHA256", zip_sha == EXPECTED_ZIP_SHA))
    with zipfile.ZipFile(path, "r") as archive:
        entries = archive.namelist()
        findings.append(("EXACT_MEMBERS", sorted(entries) == ["decision.json", "execution.log", "junit.xml"]))
        findings.append(("NO_DUPLICATE_MEMBERS", len(entries) == len(set(entries))))
        findings.append(("ZIP_CRC", archive.testzip() is None))
        if not all(name in entries for name in ("decision.json", "execution.log", "junit.xml")):
            return findings
        decision_bytes = archive.read("decision.json")
        log_bytes = archive.read("execution.log")
        junit_bytes = archive.read("junit.xml")
    findings.append(("LOG_SHA256", digest(log_bytes) == EXPECTED_LOG_SHA))
    findings.append(("JUNIT_SHA256", digest(junit_bytes) == EXPECTED_JUNIT_SHA))
    try:
        decision = json.loads(decision_bytes)
        root = ET.fromstring(junit_bytes)
        suites = [root] if root.tag == "testsuite" else root.findall("testsuite")
        totals = {key: sum(int(s.get(key, 0)) for s in suites)
                  for key in ("tests", "failures", "errors", "skipped")}
        cases = list(root.iter("testcase"))
        names = [case.get("name", "") for case in cases]
        counts = {"tests": EXPECTED_CASES, "failures": 0, "errors": 0, "skipped": 0}
        findings.extend([
            ("MISSION", decision.get("mission") == "ET665.MB.R13"),
            ("JUNIT_COUNTS", totals == counts and len(cases) == EXPECTED_CASES),
            ("DECISION_COUNTS", decision.get("test_counts") == counts),
            ("EXIT_CODE", decision.get("pytest_exit_code") == 0),
            ("LOG_AND_JUNIT_LINK", decision.get("evidence_sha256") == {
                "execution.log": digest(log_bytes), "junit.xml": digest(junit_bytes)}),
            ("FOCUSED_GATE", decision.get("gates", {}).get("focused_regressions") == "PASS"),
            ("P15_GATE", decision.get("gates", {}).get("p15_synthetic_end_to_end") == "PASS_SYNTHETIC"),
            ("P15_GUARDS", decision.get("p15_integration_and_write_guard_confirmed") is True),
            ("P15_CASES", all(
                any(n.startswith("test_full_engine_offline_with_synthetic_dataset[") and e in n for n in names)
                and any(n.startswith("test_drive_write_is_blocked_by_real_command_guard[") and e in n for n in names)
                for e in REQUIRED_ENGINES)),
            ("BLOCKED_PHASE_B", decision.get("phase_b") == "BLOCKED"),
            ("NO_REAL_ORDERS", decision.get("real_orders") == "FORBIDDEN"),
            ("NO_FTMO_REAL", decision.get("ftmo_real") == "FORBIDDEN"),
            ("RESIDUAL_NOT_CERTIFIED", decision.get("gates", {}).get("complete_residual_inventory") == "NOT_CERTIFIED"),
            ("SECURITY_NOT_CERTIFIED", decision.get("gates", {}).get("independent_security_approval") == "NOT_CERTIFIED"),
        ])
    except (ValueError, TypeError, ET.ParseError, KeyError) as exc:
        findings.append(("PARSE_AND_SCHEMA", False))
        print("VERIFICATION_ERROR:", type(exc).__name__, file=sys.stderr)
    return findings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip", required=True, type=Path)
    args = parser.parse_args()
    if not args.zip.is_file():
        raise SystemExit("ZIP_NOT_FOUND")
    try:
        findings = verify(args.zip)
    except (OSError, zipfile.BadZipFile, RuntimeError) as exc:
        print("ZIP_READ_ERROR:", type(exc).__name__, file=sys.stderr)
        return 1
    for name, passed in findings:
        print(f"{name}={'PASS' if passed else 'FAIL'}")
    print("INDEPENDENT_ARTIFACT_CHECK=" + ("PASS" if findings and all(v for _, v in findings) else "BLOCKED"))
    print("PHASE_B=BLOCKED")
    return 0 if findings and all(v for _, v in findings) else 1


if __name__ == "__main__":
    raise SystemExit(main())
