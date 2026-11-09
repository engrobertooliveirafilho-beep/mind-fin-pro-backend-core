"""ME-RS-305 offline, fail-closed regression runner. No network, Drive, or production."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
FILES = (
    "code/engineering_pipeline/post_r6.py",
    "tests/test_me_rs_303_post_r6_offline.py",
)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, help="New evidence JSON path, never overwrite")
    args = parser.parse_args()
    output = Path(args.output).resolve()
    if output.exists():
        parser.error("FAIL_CLOSED: evidence path already exists")
    if output.parent == ROOT or ROOT in output.parents:
        parser.error("FAIL_CLOSED: evidence must be written outside repository")
    hashes_before = {name: digest(ROOT / name) for name in FILES}
    command = [
        sys.executable, "-m", "unittest", "discover",
        "-s", "tests", "-p", "test_me_rs_303_post_r6_offline.py", "-v",
    ]
    started = time.time()
    result = subprocess.run(
        command, cwd=ROOT, capture_output=True, text=True,
        timeout=120, check=False,
    )
    hashes_after = {name: digest(ROOT / name) for name in FILES}
    ok = result.returncode == 0 and hashes_before == hashes_after and "Ran 10 tests" in result.stderr and "\nOK\n" in result.stderr
    report = {
        "mission": "ME-RS-305",
        "scope": "SYNTHETIC_OFFLINE_ONLY",
        "certification": "NOT_CERTIFIED",
        "result": "PASS_SYNTHETIC" if ok else "FAIL_CLOSED",
        "returncode": result.returncode,
        "elapsed_seconds": round(time.time() - started, 3),
        "sha256_before": hashes_before,
        "sha256_after": hashes_after,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "historical_r6_rows_certified": 0,
        "r4_r8_parallel_certified": False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    print(json.dumps({"result": report["result"], "evidence": str(output)}))
    return 0 if ok else 2

if __name__ == "__main__":
    raise SystemExit(main())
