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
command = [sys.executable, "-I", "-m", "unittest", "discover", "-s", str(TEST.parent), "-p", "test_et665_r*.py", "-v"]
try:
    proc = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=90)
    result = {"exit_code": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr, "timeout": False}
except subprocess.TimeoutExpired as exc:
    result = {"exit_code": 124, "stdout": (exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or ""), "stderr": (exc.stderr or b"").decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or ""), "timeout": True}
result["timestamp_utc"] = started
result["test_sha256"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(TEST.parent.glob("test_et665_r*.py"))}
result["python_version"] = sys.version.split()[0]
result["command"] = ["python", "-I", "<repository-relative-test>", "-v"]
(OUT / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
(OUT / "test.log").write_text(result["stdout"] + "\n" + result["stderr"], encoding="utf-8")
suite = ET.Element("testsuite", name="ET665_R72_offline_static", tests="1", failures="0" if result["exit_code"] == 0 else "1", errors="0", timestamp=started)
case = ET.SubElement(suite, "testcase", classname="et665_r72", name="static_regression_process")
if result["exit_code"] != 0:
    ET.SubElement(case, "failure", message="Static regression failed or timed out").text = result["stderr"][-10000:]
ET.ElementTree(suite).write(OUT / "junit.xml", encoding="utf-8", xml_declaration=True)
lines = []
for name in ("result.json", "test.log", "junit.xml"):
    p = OUT / name
    lines.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {name}")
(OUT / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"ET665_R72_STATUS={'PASS' if result['exit_code'] == 0 else 'FAIL'}; EVIDENCE={OUT}")
raise SystemExit(0 if result["exit_code"] == 0 else 1)
