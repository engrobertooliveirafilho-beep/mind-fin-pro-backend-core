import json
import subprocess
import sys
from pathlib import Path


def test_p1902f_data_acquisition_engine_runs():
    result = subprocess.run(
        [sys.executable, "_institutional/P1902F_DATA_ACQUISITION_ENGINE/data_acquisition_engine.py"],
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert result.returncode == 0, result.stderr

    base = Path("_evidence/P1902F")

    required = [
        "ACQUISITION_QUEUE.json",
        "SOURCE_DISCOVERY.json",
        "DOWNLOAD_JOBS.json",
        "NORMALIZATION_JOBS.json",
        "DATASET_TARGETS.json",
        "SPECIALIST_BACKTEST_RELINK_JOBS.json",
        "SUMMARY.json",
    ]

    for name in required:
        assert (base / name).exists(), name

    data = json.loads((base / "SUMMARY.json").read_text(encoding="utf-8"))

    assert data["program"] == "P1902F_DATA_ACQUISITION_ENGINE"
    assert data["status"] == "PASS"
    assert data["mode"] == "RESEARCH_ONLY"
    assert data["order_sent"] is False
    assert data["real_orders"] == "FORBIDDEN"
    assert data["ftmo_real"] == "FORBIDDEN"
    assert data["mt5_real"] == "FORBIDDEN"
    assert data["approved_for_P1902G"] is True
    assert data["acquisition_job_count"] > 0
    assert data["download_job_count"] == data["acquisition_job_count"]
    assert data["normalization_job_count"] == data["acquisition_job_count"]


def test_p1902f_jobs_schema():
    queue = json.loads(Path("_evidence/P1902F/ACQUISITION_QUEUE.json").read_text(encoding="utf-8"))
    downloads = json.loads(Path("_evidence/P1902F/DOWNLOAD_JOBS.json").read_text(encoding="utf-8"))
    normalizations = json.loads(Path("_evidence/P1902F/NORMALIZATION_JOBS.json").read_text(encoding="utf-8"))

    assert len(queue) > 0
    assert len(downloads) == len(queue)
    assert len(normalizations) == len(queue)

    for job in downloads:
        assert job["mode"] == "RESEARCH_ONLY"
        assert job["real_orders"] == "FORBIDDEN"
        assert "source_primary" in job
        assert "expected_format" in job

    for job in normalizations:
        assert job["mode"] == "RESEARCH_ONLY"
        assert job["real_orders"] == "FORBIDDEN"
        assert "required_validations" in job
        assert len(job["required_validations"]) >= 3
