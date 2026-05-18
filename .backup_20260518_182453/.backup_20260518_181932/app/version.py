import subprocess

def current_commit():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode().strip()
    except Exception:
        return "unknown"

RUNTIME_VERSION = {
    "commit": current_commit(),
    "runtime": "neura_human_like_runtime_v1"
}
