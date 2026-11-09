"""ET665.R335: offline-only evidence runner. No external services or order routing."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

TESTS = [
    "mind_trader/tests/test_p896_gateway_paper_broker_integration.py",
    "mind_trader/tests/test_et665_r320_paper_broker_exception.py",
    "mind_trader/tests/test_et665_r330_paper_reservation_gap.py",
    "mind_trader/tests/test_et665_r339_record_guard.py",
    "mind_trader/tests/test_et665_r344_reservation_settlement.py",
]


def main():
    root = Path(__file__).resolve().parents[2]
    output = root / "mind_trader" / "reports" / "ET665_R335_OFFLINE_EVIDENCE"
    output.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env["PYTHONPATH"] = str(root)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    cmd = [sys.executable, "-m", "pytest", "-q", "-ra", "--disable-warnings", *TESTS]
    missing = [name for name in TESTS if not (root / name).is_file()]
    try:
        if missing:
            raise FileNotFoundError("Missing test sources: " + ", ".join(missing))
        completed = subprocess.run(cmd, cwd=root, env=env, capture_output=True, text=True, timeout=180)
        result = completed.returncode
        log = completed.stdout + "\n--- STDERR ---\n" + completed.stderr
    except subprocess.TimeoutExpired as exc:
        result = 124
        log = "TIMEOUT: " + repr(exc)
    except (OSError, ValueError) as exc:
        result = 125
        log = "PREFLIGHT_OR_EXECUTION_ERROR: " + repr(exc)
    log_path = output / "pytest.log"
    log_path.write_text(log, encoding="utf-8")
    digest = hashlib.sha256(log_path.read_bytes()).hexdigest()
    source_hashes = {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in TESTS if (root / name).is_file()}
    expected_failures = "xfailed" in log.lower() or "xpass" in log.lower()
    status = "FAIL_OR_BLOCKED" if result != 0 else ("PASS_WITH_KNOWN_GAPS" if expected_failures else "PASS_TEST_SCOPE_ONLY")
    report = {
        "phase": "ET665.R335", "utc": datetime.now(timezone.utc).isoformat(),
        "scope": "PAPER tests only", "real_orders": "FORBIDDEN",
        "command": cmd, "exit_code": result, "log_sha256": digest,
        "test_source_sha256": source_hashes,
        "status": status,
        "known_gaps_present": expected_failures,
        "missing_test_sources": missing,
        "note": "No network/process isolation is enforced by this runner. Not a Docker isolation or global certification result.",
    }
    (output / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return result


if __name__ == "__main__":
    raise SystemExit(main())
