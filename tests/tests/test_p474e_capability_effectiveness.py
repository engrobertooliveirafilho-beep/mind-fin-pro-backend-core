import json
import subprocess
import sys

def test_p474e_effectiveness_score_runs():

    result = subprocess.run(
        [
            sys.executable,
            "tools/capability_effectiveness_score.py"
        ],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0

    data = json.loads(
        result.stdout if result.stdout.strip() else "{}"
    )

    assert isinstance(data, dict)
