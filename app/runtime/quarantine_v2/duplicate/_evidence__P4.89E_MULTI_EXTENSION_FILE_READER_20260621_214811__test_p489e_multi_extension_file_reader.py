import json
from pathlib import Path

def test_p489e_multi_extension_file_reader():
    report = json.loads(Path("runtime/file_ingestion/readers/multi_extension_reader_report.json").read_text(encoding="utf-8"))

    assert report["milestone"] == "P4.89E COMPLETE"
    assert report["reader"] == "MULTI_EXTENSION_FILE_READER"
    assert report["mode"] == "SAFE_READ_AND_METADATA_ONLY"
    assert report["physical_move"] == "NOT_EXECUTED"
    assert report["delete"] == "FORBIDDEN"
    assert report["total_files_checked"] >= 1

    assert ".py" in report["supported_text_extensions"]
    assert ".json" in report["supported_text_extensions"]
    assert ".pdf" in report["specialized_parser_extensions"]
    assert ".docx" in report["specialized_parser_extensions"]
    assert ".xlsx" in report["specialized_parser_extensions"]
    assert ".pptx" in report["specialized_parser_extensions"]
    assert ".png" in report["image_extensions_metadata_only"]
