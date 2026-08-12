import json
from pathlib import Path

from subprocess import run
import sys

def test_p481_runtime_review_queue_builds():
    result = run(
        [sys.executable, "tools/build_runtime_review_queue.py"],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0

    q = Path("runtime/review_queue/runtime_review_queue.json")
    assert q.exists()

    data = json.loads(q.read_text(encoding="utf-8"))
    assert data["engine"] == "P4.81_RUNTIME_REVIEW_QUEUE"
    assert "items" in data
    assert isinstance(data["items"], list)
