import json
from pathlib import Path

def test_p489f_content_extraction_to_knowledge():

    data = json.loads(
        Path(
            "runtime/knowledge_extraction/extracted_knowledge.json"
        ).read_text(encoding="utf-8")
    )

    report = data["report"]

    assert report["milestone"] == "P4.89F COMPLETE"
    assert report["engine"] == "CONTENT_EXTRACTION_TO_KNOWLEDGE"
    assert report["mode"] == "READ_ONLY_EXTRACTION"
    assert report["physical_move"] == "NOT_EXECUTED"
    assert report["delete"] == "FORBIDDEN"

    assert isinstance(data["knowledge"], list)

    queue = json.loads(
        Path(
            "runtime/knowledge_extraction/queue/knowledge_queue.json"
        ).read_text(encoding="utf-8")
    )

    assert isinstance(queue, list)
