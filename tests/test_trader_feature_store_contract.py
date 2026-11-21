import json
from pathlib import Path
from copy import deepcopy
from app.runtime.trader_feature_store_contract import validate_feature_definitions, validate_feature_record, validate_feature_batch

DEFS = json.loads((Path(__file__).parents[1] / "app/data/trader_feature_definitions_v1.json").read_text())

def valid_record(ts="2026-07-23T21:00:00Z"):
    features = {}
    for d in DEFS:
        if d["dtype"] == "bool": features[d["feature"]] = False
        elif d["dtype"] == "string": features[d["feature"]] = "LONDON"
        elif d["dtype"] == "int8": features[d["feature"]] = 1
        else: features[d["feature"]] = 1.25
    return {
        "canonical_symbol": "GER40_CASH", "timeframe": "M1", "timestamp_utc": ts,
        "source_run_id": "20260719_074124", "source_path": "lake/raw/GER40_M1.csv",
        "source_sha256": "a" * 64, "normalizer_version": "1.0.0",
        "feature_definition_version": "TRADER.1.FEATURE.STORE.V1", "feature_contract": "TRADER.1.FEATURE.STORE.V1",
        "features": features,
    }

def test_drive_catalog_has_42_causal_definitions():
    result = validate_feature_definitions(DEFS, expected_count=42)
    assert result["passed"] is True and result["count"] == 42

def test_future_offset_rejected():
    defs = deepcopy(DEFS); defs[0]["future_offset"] = 1
    assert "FUTURE_OFFSET_FORBIDDEN:return_1" in validate_feature_definitions(defs, 42)["errors"]

def test_negative_lag_rejected():
    defs = deepcopy(DEFS); defs[0]["lag"] = -1
    assert "NEGATIVE_LAG_FORBIDDEN:return_1" in validate_feature_definitions(defs, 42)["errors"]

def test_duplicate_definition_rejected():
    defs = deepcopy(DEFS); defs[1] = deepcopy(defs[0])
    assert any(e.startswith("DUPLICATE_FEATURE_DEFINITION") for e in validate_feature_definitions(defs, 42)["errors"])

def test_valid_market_feature_record_passes():
    assert validate_feature_record(valid_record(), DEFS) == []

def test_metadata_only_trader_1006_record_rejected():
    metadata = {"artifact_class":"EVIDENCE", "feature_set":"TRADER_1_006_CERTIFIED_ARTIFACT_METADATA", "feature_id":"FEATURE_00000001", "run_id":"TRADER_1_006_CONTROLLED_RUN_20260723_215100", "immutable_source":True}
    errors = validate_feature_record(metadata, DEFS)
    assert any("MISSING_FEATURE_FIELDS" in e for e in errors)

def test_naive_timestamp_rejected():
    record = valid_record("2026-07-23T21:00:00")
    assert "TIMESTAMP_MUST_BE_UTC" in validate_feature_record(record, DEFS)

def test_non_utc_offset_rejected():
    record = valid_record("2026-07-23T18:00:00-03:00")
    assert "TIMESTAMP_MUST_BE_UTC" in validate_feature_record(record, DEFS)

def test_missing_feature_value_rejected():
    record = valid_record(); record["features"].pop("atr_14")
    assert any(e.startswith("MISSING_FEATURE_VALUES") for e in validate_feature_record(record, DEFS))

def test_nan_feature_rejected():
    record = valid_record(); record["features"]["atr_14"] = float("nan")
    assert "INVALID_NUMERIC_FEATURE:atr_14" in validate_feature_record(record, DEFS)

def test_warmup_null_allowed():
    record = valid_record(); record["features"]["sma_200"] = None
    assert validate_feature_record(record, DEFS) == []

def test_invalid_source_hash_rejected():
    record = valid_record(); record["source_sha256"] = "not-a-hash"
    assert "INVALID_SOURCE_SHA256" in validate_feature_record(record, DEFS)

def test_duplicate_primary_key_rejected():
    record = valid_record()
    result = validate_feature_batch([record, deepcopy(record)], DEFS)
    assert result["passed"] is False and any(e.startswith("DUPLICATE_PRIMARY_KEY") for e in result["errors"])

def test_non_chronological_batch_rejected():
    later = valid_record("2026-07-23T21:02:00Z")
    earlier = valid_record("2026-07-23T21:01:00Z")
    result = validate_feature_batch([later, earlier], DEFS)
    assert result["passed"] is False and any(e.startswith("NON_CHRONOLOGICAL_SERIES") for e in result["errors"])

def test_valid_batch_never_promotes_automatically():
    first = valid_record("2026-07-23T21:00:00Z")
    second = valid_record("2026-07-23T21:01:00Z")
    result = validate_feature_batch([first, second], DEFS)
    assert result["passed"] is True and result["promotion_allowed"] is False
