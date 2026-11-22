import pytest
from app.runtime.p2383_walk_forward_contract import chronological_folds

def rows(n=500):
    return [{"signal_id":f"S{i:04d}","entry_time":f"2025-01-{1+i//24:02d} {i%24:02d}:00:00",
             "realized_r":(-1.0 if i%3==0 else 2.0),"family":"F",
             "mode":"PAPER_ONLY","real_orders":"FORBIDDEN","ftmo_real":"FORBIDDEN",
             "warning":"PAPER_FEEDBACK_PROXY_NOT_REAL_PNL"} for i in range(n)]

def test_full_population_splits_into_five_strict_folds():
    r=chronological_folds(rows(),source_mission="P2380_DE40_FORWARD_PAPER_FEEDBACK_LOOP_AND_PNL_TRACKING")
    assert r["source_rows"]==500 and r["initial_train_rows"]==250 and len(r["folds"])==5
    for f in r["folds"]:
        assert f["train_rows"] and f["test_rows"]
        assert f["train_end"] < f["test_start"]
    assert not r["performance_certified"] and not r["promotion_allowed"]

@pytest.mark.parametrize("n",[227,499,501])
def test_partial_or_survivor_population_rejected(n):
    with pytest.raises(ValueError,match="500_ROW"):
        chronological_folds(rows(n),source_mission="P2380_DE40_FORWARD_PAPER_FEEDBACK_LOOP_AND_PNL_TRACKING")

def test_p2382_survivors_cannot_be_source():
    with pytest.raises(ValueError,match="WRONG_SOURCE"):
        chronological_folds(rows(),source_mission="P2382_DE40_REPLAY_AFTER_LOSS_PATCH")

def test_duplicate_signal_rejected():
    x=rows();x[1]["signal_id"]=x[0]["signal_id"]
    with pytest.raises(ValueError,match="DUPLICATE"):
        chronological_folds(x,source_mission="P2380_DE40_FORWARD_PAPER_FEEDBACK_LOOP_AND_PNL_TRACKING")

def test_invalid_timestamp_rejected():
    x=rows();x[0]["entry_time"]="unknown"
    with pytest.raises(ValueError,match="ENTRY_TIME"):
        chronological_folds(x,source_mission="P2380_DE40_FORWARD_PAPER_FEEDBACK_LOOP_AND_PNL_TRACKING")

def test_nonfinite_outcome_rejected():
    x=rows();x[0]["realized_r"]="NaN"
    with pytest.raises(ValueError,match="REALIZED_R"):
        chronological_folds(x,source_mission="P2380_DE40_FORWARD_PAPER_FEEDBACK_LOOP_AND_PNL_TRACKING")


def test_partial_safety_metadata_rejected():
    x = rows()
    del x[0]["ftmo_real"]
    with pytest.raises(ValueError, match="INCOMPLETE_PAPER_SAFETY"):
        chronological_folds(x, source_mission="P2380_DE40_FORWARD_PAPER_FEEDBACK_LOOP_AND_PNL_TRACKING")


@pytest.mark.parametrize("field,value", [
    ("mode", "LIVE"),
    ("real_orders", "ALLOWED"),
    ("ftmo_real", "ALLOWED"),
    ("warning", "REAL_PNL"),
])
def test_unsafe_canonical_metadata_rejected(field, value):
    x = rows()
    for row in x:
        row.update(mode="PAPER_ONLY", real_orders="FORBIDDEN",
                   ftmo_real="FORBIDDEN", warning="PAPER_FEEDBACK_PROXY_NOT_REAL_PNL")
    x[0][field] = value
    with pytest.raises(ValueError, match="UNSAFE_OR_NONPROXY"):
        chronological_folds(x, source_mission="P2380_DE40_FORWARD_PAPER_FEEDBACK_LOOP_AND_PNL_TRACKING")


def test_equal_timestamp_at_train_test_boundary_rejected():
    x = rows()
    x[250]["entry_time"] = x[249]["entry_time"]
    with pytest.raises(ValueError, match="TEMPORAL_TIE"):
        chronological_folds(x, source_mission="P2380_DE40_FORWARD_PAPER_FEEDBACK_LOOP_AND_PNL_TRACKING")


def test_equal_timestamp_inside_one_fold_allowed():
    x = rows()
    x[251]["entry_time"] = x[250]["entry_time"]
    result = chronological_folds(x, source_mission="P2380_DE40_FORWARD_PAPER_FEEDBACK_LOOP_AND_PNL_TRACKING")
    assert len(result["folds"]) == 5


def test_mixed_canonical_and_legacy_schema_rejected():
    x = rows()
    for key in ("mode", "real_orders", "ftmo_real", "warning"):
        del x[0][key]
    with pytest.raises(ValueError, match="INCOMPLETE_PAPER_SAFETY"):
        chronological_folds(x, source_mission="P2380_DE40_FORWARD_PAPER_FEEDBACK_LOOP_AND_PNL_TRACKING")


@pytest.mark.parametrize("bad_id", [[], {}, 123, " ", None])
def test_malformed_signal_id_rejected(bad_id):
    x = rows()
    x[0]["signal_id"] = bad_id
    with pytest.raises(ValueError, match="DUPLICATE_OR_MISSING_SIGNAL_ID"):
        chronological_folds(x, source_mission="P2380_DE40_FORWARD_PAPER_FEEDBACK_LOOP_AND_PNL_TRACKING")


def test_entire_population_without_paper_safety_rejected():
    x = rows()
    for row in x:
        for key in ("mode", "real_orders", "ftmo_real", "warning"):
            del row[key]
    with pytest.raises(ValueError, match="INCOMPLETE_PAPER_SAFETY"):
        chronological_folds(x, source_mission="P2380_DE40_FORWARD_PAPER_FEEDBACK_LOOP_AND_PNL_TRACKING")
