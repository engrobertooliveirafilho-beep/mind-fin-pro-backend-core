import json
from pathlib import Path

def test_p491b_zip_archive_reader_extractor():
    index = json.loads(Path("runtime/archive_ingestion/zip_index/zip_archive_index.json").read_text(encoding="utf-8"))
    ledger = json.loads(Path("runtime/archive_ingestion/zip_extraction_ledger.json").read_text(encoding="utf-8"))

    assert index["milestone"] == "P4.91B COMPLETE"
    assert index["engine"] == "ZIP_ARCHIVE_READER_AND_EXTRACTOR"
    assert index["mode"] == "SAFE_ZIP_INDEX_AND_LIMITED_EXTRACT"
    assert index["delete_original_zip"] == "FORBIDDEN"
    assert index["move_original_zip"] == "FORBIDDEN"

    assert ledger["milestone"] == "P4.91B COMPLETE"
    assert ledger["extraction"] == "SAFE_LIMITED_ZIP_EXTRACTION"
    assert ledger["extracted_count"] >= 0
    assert ledger["errors_count"] >= 0

    for item in ledger["extracted"]:
        assert item["delete_original_zip"] is False
        assert item["physical_move_original_zip"] == "NOT_EXECUTED"
        assert Path(item["target"]).exists()
