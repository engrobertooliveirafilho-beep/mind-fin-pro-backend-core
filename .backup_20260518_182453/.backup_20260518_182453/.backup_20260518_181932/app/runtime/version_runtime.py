import subprocess

def runtime_version():
    try:
        commit = subprocess.check_output(
            ["git","rev-parse","--short","HEAD"],
            text=True
        ).strip()
    except Exception:
        commit = "unknown"

    return {
        "commit": commit,
        "runtime": "neura_runtime_live"
    }
