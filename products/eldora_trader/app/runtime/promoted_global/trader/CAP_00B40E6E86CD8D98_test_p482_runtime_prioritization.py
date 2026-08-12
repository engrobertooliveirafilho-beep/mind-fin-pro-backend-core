import json
from pathlib import Path
import subprocess
import sys

def test_p482_prioritization_generates_queue():
    input_path = Path("runtime/review_queue/runtime_review_queue.json")
    assert input_path.exists(), "runtime_review_queue.json ausente"

    result = subprocess.run(
        [sys.executable, "tools/build_runtime_prioritized_queue.py"],
        capture_output=True,
        text=True,
        check=True
    )

    output_path = Path("runtime/prioritization/runtime_prioritized_queue.json")
    assert output_path.exists(), "runtime_prioritized_queue.json não foi criado"

    data = json.loads(output_path.read_text(encoding="utf-8"))

    assert data["milestone"] == "P4.82 COMPLETE"
    assert data["engine"] == "AUTO_PRIORITIZATION"
    assert data["execution_policy"]["automatic_implementation"] == "FORBIDDEN"
    assert data["execution_policy"]["review_required"] is True
    assert data["execution_policy"]["approval_required"] is True

    queue = data["queue"]
    assert isinstance(queue, list)
    assert data["total_missions"] == len(queue)

    for item in queue:
        assert item["status"] == "PENDING_REVIEW"
        assert item["approval_required"] is True
        assert item["auto_execution_allowed"] is False
        assert 1 <= item["priority_score"] <= 10
        assert item["priority_band"] in ["P0_CRITICAL", "P1_HIGH", "P2_MEDIUM", "P3_LOW"]
        assert "impact" in item["scoring"]
        assert "risk" in item["scoring"]
        assert "dependencies" in item["scoring"]
        assert "complexity" in item["scoring"]
        assert "expected_value" in item["scoring"]

    scores = [x["priority_score"] for x in queue]
    assert scores == sorted(scores, reverse=True)
