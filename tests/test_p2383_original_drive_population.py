import csv
import hashlib
import os
from pathlib import Path

import pytest

from app.runtime.p2383_walk_forward_contract import chronological_folds

EXPECTED_SHA256 = "31aa0c813150b249aa6c653971dbb5f9766b6905c642807e81796d455bd4c197"
MISSION = "P2380_DE40_FORWARD_PAPER_FEEDBACK_LOOP_AND_PNL_TRACKING"


def test_original_drive_p2380_csv_walk_forward():
    path_value = os.environ.get("P2380_FEEDBACK_CSV")
    if not path_value:
        pytest.skip("P2380_FEEDBACK_CSV not supplied")
    path = Path(path_value)
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == EXPECTED_SHA256
    rows = list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))
    assert len(rows) == 500
    assert len({row["signal_id"] for row in rows}) == 500
    assert all(row["mode"] == "PAPER_ONLY" for row in rows)
    assert all(row["real_orders"] == "FORBIDDEN" for row in rows)
    assert all(row["ftmo_real"] == "FORBIDDEN" for row in rows)
    assert all(row["warning"] == "PAPER_FEEDBACK_PROXY_NOT_REAL_PNL" for row in rows)

    result = chronological_folds(rows, source_mission=MISSION)
    assert result["status"] == "CHRONOLOGICAL_SPLIT_READY_NOT_PERFORMANCE_CERTIFIED"
    assert result["initial_train_rows"] == 250
    assert [len(fold["test_rows"]) for fold in result["folds"]] == [50] * 5
    assert all(fold["train_end"] < fold["test_start"] for fold in result["folds"])
    assert result["p2382_survivors_allowed_as_primary_input"] is False
    assert result["performance_certified"] is False
    assert result["promotion_allowed"] is False
