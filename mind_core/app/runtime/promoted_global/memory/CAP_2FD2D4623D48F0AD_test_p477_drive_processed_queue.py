from pathlib import Path

from app.runtime.drive_processed_queue import process_file, already_processed

def test_p477_process_file_once(tmp_path):
    f = tmp_path / "doc.txt"
    f.write_text("pgvector retrieval semantic_route social memory", encoding="utf-8")

    out = process_file(str(f), move=True)

    assert out["status"] == "processed"
    assert out["absorption"]["matched"] is True
    assert already_processed(str(f)) is True
