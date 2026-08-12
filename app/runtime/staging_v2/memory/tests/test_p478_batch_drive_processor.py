from pathlib import Path
from app.runtime.drive_batch_processor import process_folder

def test_p478_batch_processor(tmp_path):
    f = tmp_path / "doc.txt"
    f.write_text("pgvector retrieval semantic_route social memory", encoding="utf-8")
    out = process_folder(str(tmp_path), recursive=True)
    assert out["total_seen"] >= 1
    assert out["processed"] >= 1
