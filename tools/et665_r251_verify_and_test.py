"""ET665.R251 — Verify exact Git blob identity before offline regression execution.

Usage (from repository root):
  python tools/et665_r251_verify_and_test.py

No broker, network, cloud or real execution. Fails closed on any mismatch.
Pinned to the audited R249 source at GitHub commit b4d2e3b4fecb3e5e47b63a796932893258b2293e.
"""
import hashlib
import pathlib
import subprocess
import sys

EXPECTED = {
    "app/runtime/et665_r246_mtm_ensemble_audit.py": "45b7b63785fba162861a40d8e7c11b3916b02c55",
    "tests/test_et665_r246_mtm_ensemble.py": "41dcfffe552405fbbf6f0ce6ddf6ca6dd07585cc",
}

def git_blob_sha(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\\0" + data).hexdigest()

def main():
    root = pathlib.Path(__file__).resolve().parents[1]
    for name, expected in EXPECTED.items():
        path = root / name
        if not path.is_file():
            raise SystemExit("FAIL_CLOSED: missing " + name)
        raw = path.read_bytes()
        actual = git_blob_sha(raw)
        print(name, "blob_sha", actual, "sha256", hashlib.sha256(raw).hexdigest())
        if actual != expected:
            raise SystemExit("FAIL_CLOSED: Git blob mismatch " + name)
    print("PROVENANCE_MATCH: 2/2")
    cmd = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
           "tests/test_et665_r246_mtm_ensemble.py"]
    print("RUN:", " ".join(cmd))
    return subprocess.call(cmd, cwd=str(root))

if __name__ == "__main__":
    sys.exit(main())
