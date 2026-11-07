"""ET665.MB.R8: one-shot offline consolidated regression evidence runner. Never grants trading authorization."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
TESTS = [
    "mind_trader/tests/test_et665_cm2_residual_guards.py",
    "mind_trader/tests/test_et665_cm5_mt5_fail_closed.py",
    "mind_trader/tests/test_et665_cm6_evidence_stager.py",
    "mind_trader/tests/test_et665_cm7_p15_offline_exports.py",
    "mind_trader/tests/test_et665_cm7_stager_integration.py",
    "mind_trader/tests/test_et665_mb_p15_synthetic_integration.py",
    "mind_trader/tests/security_review/test_et665_mb_r2_adapter_malformed.py",
    "mind_trader/tests/security_review/test_et665_mb_r3_ftmo_config_failclosed.py",
    "mind_trader/tests/security_review/test_et665_mb_r4_paper_session_corruption.py",
    "mind_trader/tests/security_review/test_et665_mb_r5_paper_pnl_integrity.py",
    "mind_trader/tests/security_review/test_et665_mb_r6_paper_fill_safety.py",
    "mind_trader/tests/security_review/test_et665_mb_r7_ftmo_cost_constraints.py",
    "mind_trader/tests/security_review/test_et665_mb_r9_adversarial_context_failclosed.py",
]
REQUIRED = 224

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    out = Path(args.output).resolve()
    temp_root = Path(os.environ.get("TEMP", os.environ.get("TMP", "/tmp"))).resolve()
    if temp_root not in out.parents:
        raise SystemExit("ET665_MB_OUTPUT_MUST_BE_TEMP_SUBDIRECTORY")
    archive = out.parent / (out.name + ".zip")
    if archive.exists():
        raise SystemExit("ET665_MB_ZIP_NO_OVERWRITE")
    if out.exists():
        raise SystemExit("ET665_MB_NO_OVERWRITE")
    out.mkdir(parents=True)
    env = os.environ.copy()
    env.update(PYTEST_DISABLE_PLUGIN_AUTOLOAD="1", PYTHONDONTWRITEBYTECODE="1", PYTHONPATH=str(ROOT))
    command = [sys.executable, "-m", "pytest", "-q", *TESTS, "--junitxml=" + str(out / "junit.xml")]
    try:
        result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, timeout=180)
        output_text = result.stdout + "\n" + result.stderr
        return_code = result.returncode
    except subprocess.TimeoutExpired as exc:
        output_text = "ET665_MB_TIMEOUT_180_SECONDS\\n"
        return_code = 124
    (out / "execution.log").write_text(output_text, encoding="utf-8")
    counts = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0}
    junit = out / "junit.xml"
    if junit.exists():
        try:
            tree = ET.parse(junit)
            suites = [tree.getroot()] if tree.getroot().tag == "testsuite" else tree.getroot().findall("testsuite")
            for suite in suites:
                for key in counts:
                    counts[key] += int(suite.get(key, 0))
        except (ET.ParseError, ValueError):
            return_code = 125
    focused = return_code == 0 and counts == dict(tests=REQUIRED, failures=0, errors=0, skipped=0)
    # Per-case JUnit proof: a suite-wide PASS cannot hide missing P15 cases.
    case_names = set()
    if junit.exists() and return_code == 0:
        for testcase in tree.getroot().iter("testcase"):
            case_names.add(testcase.get("name", ""))
    required_engines = ("p1516", "p1525b", "p153_p155", "p156_p1510")
    integrated = focused and all(
        any(name.startswith("test_full_engine_offline_with_synthetic_dataset[") and engine in name for name in case_names)
        and any(name.startswith("test_drive_write_is_blocked_by_real_command_guard[") and engine in name for name in case_names)
        for engine in required_engines
    )
    # Deliberately fail-closed: focused tests do not establish integrated runtime,
    # comprehensive security review, or formal authorization.
    gates = {
        "focused_regressions": "PASS" if focused else "BLOCKED",
        "p15_synthetic_end_to_end": "PASS_SYNTHETIC" if integrated else "BLOCKED",
        "complete_residual_inventory": "NOT_CERTIFIED",
        "independent_security_approval": "NOT_CERTIFIED",
        "governed_github_publication": "NOT_CERTIFIED",
    }
    evidence = {
        "mission": "ET665.MB.R9", "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "test_counts": counts, "pytest_exit_code": return_code,
        "required_p15_engine_ids": list(required_engines),
        "p15_integration_and_write_guard_confirmed": integrated,
        "gates": gates, "phase_b": "BLOCKED",
        "real_orders": "FORBIDDEN", "ftmo_real": "FORBIDDEN",
        "evidence_sha256": {p.name: sha(p) for p in (out / "execution.log", junit) if p.exists()},
    }
    (out / "decision.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(out.iterdir()):
            z.write(p, arcname=p.name)
    print(json.dumps({"phase_b": "BLOCKED", "focused": gates["focused_regressions"],
                      "tests": counts, "zip": str(archive), "zip_sha256": sha(archive)}))
    return 0 if focused and integrated else 1

if __name__ == "__main__":
    raise SystemExit(main())
