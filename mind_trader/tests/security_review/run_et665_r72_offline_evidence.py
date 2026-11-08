"""R72: stdlib-only offline test runner; no network or trading imports."""
import hashlib
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TEST = ROOT / "mind_trader/tests/security_review/test_et665_r69_consolidated_static_regression.py"
OUT = ROOT / "mind_trader/audits/local_evidence/et665_r72"
OUT.mkdir(parents=True, exist_ok=True)
started = datetime.now(timezone.utc).isoformat()
# Use interpreter isolation (-I), with explicit timeout and no inherited PYTHONPATH.
tests = [TEST, TEST.parent / "test_et665_r77_paper_gateway_isolated.py", TEST.parent / "test_et665_r82_paper_broker_fill_isolated.py", TEST.parent / "test_et665_r84_paper_jsonl_integration.py", TEST.parent / "test_et665_r86_gateway_broker_jsonl.py", TEST.parent / "test_et665_r90_paper_session_accounting_gap.py", TEST.parent / "test_et665_r92_session_recording_contract.py", TEST.parent / "test_et665_r95_atomic_capacity.py", TEST.parent / "test_et665_r99_capacity_recovery.py", TEST.parent / "test_et665_r101_sqlite_process_crash.py", TEST.parent / "test_et665_r104_multiprocess_capacity.py", TEST.parent / "test_et665_r106_ledger_reconciliation.py", TEST.parent / "test_et665_r108_actual_broker_schema.py", TEST.parent / "test_et665_r110_offline_paper_correlation.py", TEST.parent / "test_et665_r113_gateway_capacity_integration.py"]
runs = []
for test in tests:
    command = [sys.executable, "-I", str(test), "-v"]
    try:
        proc = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=90)
        runs.append({"test": test.name, "exit_code": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr, "timeout": False})
    except subprocess.TimeoutExpired as exc:
        runs.append({"test": test.name, "exit_code": 124, "stdout": (exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or ""), "stderr": (exc.stderr or b"").decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or ""), "timeout": True})
result = {"exit_code": 0 if all(run["exit_code"] == 0 for run in runs) else 1,
          "stdout": "\n".join(run["stdout"] for run in runs),
          "stderr": "\n".join(run["stderr"] for run in runs),
          "timeout": any(run["timeout"] for run in runs),
          "runs": runs}
result["timestamp_utc"] = started
evidence_sources = tests + [TEST.parent / "et665_r95_atomic_capacity_prototype.py", TEST.parent / "et665_r113_paper_capacity_gate.py", Path(__file__)]
result["test_sha256"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in evidence_sources}
result["python_version"] = sys.version.split()[0]
result["command"] = ["python", "-I", "<each-pinned-test>", "-v"]
(OUT / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
(OUT / "test.log").write_text(result["stdout"] + "\n" + result["stderr"], encoding="utf-8")
suite = ET.Element("testsuite", name="ET665_R80_offline_regressions", tests=str(len(runs)),
                   failures=str(sum(run["exit_code"] != 0 for run in runs)), errors="0", timestamp=started)
for run in runs:
    case = ET.SubElement(suite, "testcase", classname="et665_offline", name=run["test"])
    ET.SubElement(case, "system-out").text = run["stdout"][-20000:]
    if run["exit_code"] != 0:
        ET.SubElement(case, "failure", message="Offline test process failed or timed out").text = run["stderr"][-20000:]
ET.ElementTree(suite).write(OUT / "junit.xml", encoding="utf-8", xml_declaration=True)
lines = []
for name in ("result.json", "test.log", "junit.xml"):
    p = OUT / name
    lines.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {name}")
(OUT / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"ET665_R72_STATUS={'PASS' if result['exit_code'] == 0 else 'FAIL'}; EVIDENCE={OUT}")
raise SystemExit(0 if result["exit_code"] == 0 else 1)
