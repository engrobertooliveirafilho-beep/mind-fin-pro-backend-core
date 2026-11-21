"""Fail-closed validation for TRADER.1.FEATURE.STORE.V1 records.

Validates feature materialization output; does not calculate features, mutate the
raw data lake, promote strategies, or authorize live execution.
"""
from __future__ import annotations

import math
import re
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping

CONTRACT_ID = "TRADER.1.FEATURE.STORE.V1"
_ALLOWED_DTYPES = {"float64", "int8", "string", "bool"}
_SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")


def _finite_number(value: Any) -> bool:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    try:
        return math.isfinite(float(value))
    except (OverflowError, TypeError, ValueError):
        return False


def _parse_utc(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None or parsed.utcoffset().total_seconds() != 0:
        return None
    return parsed.astimezone(timezone.utc)


def validate_feature_definitions(definitions: Iterable[Mapping[str, Any]], expected_count: int = 42) -> dict:
    errors: list[str] = []
    if not isinstance(definitions, (list, tuple)):
        return {"passed": False, "errors": ["INVALID_DEFINITIONS_COLLECTION"], "count": 0}
    seen: set[str] = set()
    for index, definition in enumerate(definitions):
        if not isinstance(definition, Mapping):
            errors.append(f"INVALID_DEFINITION:{index}")
            continue
        name = definition.get("feature")
        if not isinstance(name, str) or not name.strip():
            errors.append(f"INVALID_FEATURE_NAME:{index}")
            continue
        if name in seen:
            errors.append(f"DUPLICATE_FEATURE_DEFINITION:{name}")
        seen.add(name)
        if definition.get("dtype") not in _ALLOWED_DTYPES:
            errors.append(f"UNSUPPORTED_DTYPE:{name}")
        for field in ("window", "min_history", "lag", "future_offset"):
            if type(definition.get(field)) is not int:
                errors.append(f"INVALID_DEFINITION_INTEGER:{name}:{field}")
        if type(definition.get("window")) is int and definition["window"] < 1:
            errors.append(f"INVALID_WINDOW:{name}")
        if type(definition.get("min_history")) is int and type(definition.get("window")) is int and definition["min_history"] < definition["window"]:
            errors.append(f"INSUFFICIENT_MIN_HISTORY:{name}")
        if type(definition.get("lag")) is int and definition["lag"] < 0:
            errors.append(f"NEGATIVE_LAG_FORBIDDEN:{name}")
        if type(definition.get("future_offset")) is int and definition["future_offset"] > 0:
            errors.append(f"FUTURE_OFFSET_FORBIDDEN:{name}")
        if definition.get("centered_window") is True:
            errors.append(f"CENTERED_WINDOW_FORBIDDEN:{name}")
    if expected_count is not None and len(seen) != expected_count:
        errors.append(f"FEATURE_COUNT_MISMATCH:expected={expected_count}:actual={len(seen)}")
    return {"passed": not errors, "errors": errors, "count": len(seen), "contract": CONTRACT_ID}


def validate_feature_record(record: Mapping[str, Any], definitions: Iterable[Mapping[str, Any]]) -> list[str]:
    errors: list[str] = []
    if not isinstance(record, Mapping):
        return ["INVALID_FEATURE_RECORD"]
    required = ("canonical_symbol", "timeframe", "timestamp_utc", "source_run_id", "source_path", "source_sha256", "normalizer_version", "feature_definition_version", "feature_contract", "features")
    missing = [field for field in required if field not in record]
    if missing:
        errors.append("MISSING_FEATURE_FIELDS:" + ",".join(missing))
        return errors
    if record.get("feature_contract") != CONTRACT_ID:
        errors.append("FEATURE_CONTRACT_MISMATCH")
    for field in ("canonical_symbol", "timeframe", "source_run_id", "source_path", "normalizer_version", "feature_definition_version"):
        if not isinstance(record.get(field), str) or not record[field].strip():
            errors.append(f"INVALID_PROVENANCE_FIELD:{field}")
    if not _SHA256_RE.fullmatch(str(record.get("source_sha256", ""))):
        errors.append("INVALID_SOURCE_SHA256")
    if _parse_utc(record.get("timestamp_utc")) is None:
        errors.append("TIMESTAMP_MUST_BE_UTC")

    definition_map = {d["feature"]: d for d in definitions if isinstance(d, Mapping) and isinstance(d.get("feature"), str)}
    values = record.get("features")
    if not isinstance(values, Mapping):
        errors.append("FEATURE_CONTAINER_REQUIRED_METADATA_NOT_FEATURES")
        return errors
    missing_features = sorted(set(definition_map) - set(values))
    extra_features = sorted(set(values) - set(definition_map))
    if missing_features:
        errors.append("MISSING_FEATURE_VALUES:" + ",".join(missing_features))
    if extra_features:
        errors.append("UNDECLARED_FEATURE_VALUES:" + ",".join(extra_features))
    for name, value in values.items():
        definition = definition_map.get(name)
        if definition is None or value is None:
            # Warm-up nulls are explicitly allowed by the source contract.
            continue
        dtype = definition.get("dtype")
        if dtype in ("float64", "int8") and not _finite_number(value):
            errors.append(f"INVALID_NUMERIC_FEATURE:{name}")
        elif dtype == "string" and (not isinstance(value, str) or not value.strip()):
            errors.append(f"INVALID_STRING_FEATURE:{name}")
        elif dtype == "bool" and type(value) is not bool:
            errors.append(f"INVALID_BOOLEAN_FEATURE:{name}")
    return errors


def validate_feature_batch(records: Iterable[Mapping[str, Any]], definitions: Iterable[Mapping[str, Any]]) -> dict:
    errors: list[str] = []
    if not isinstance(records, (list, tuple)):
        return {"passed": False, "errors": ["INVALID_FEATURE_BATCH"], "records": 0, "promotion_allowed": False}
    definitions = list(definitions)
    definition_result = validate_feature_definitions(definitions, expected_count=len(definitions))
    errors.extend("DEFINITION:" + e for e in definition_result["errors"])
    seen: set[tuple[str, str, str]] = set()
    last_by_series: dict[tuple[str, str], datetime] = {}
    for index, record in enumerate(records):
        record_errors = validate_feature_record(record, definitions)
        errors.extend(f"RECORD:{index}:{e}" for e in record_errors)
        if not isinstance(record, Mapping):
            continue
        symbol, timeframe, timestamp = record.get("canonical_symbol"), record.get("timeframe"), record.get("timestamp_utc")
        parsed = _parse_utc(timestamp)
        if isinstance(symbol, str) and isinstance(timeframe, str) and parsed is not None:
            pk = (symbol, timeframe, parsed.isoformat())
            if pk in seen:
                errors.append("DUPLICATE_PRIMARY_KEY:" + "|".join(pk))
            seen.add(pk)
            series = (symbol, timeframe)
            previous = last_by_series.get(series)
            if previous is not None and parsed <= previous:
                errors.append(f"NON_CHRONOLOGICAL_SERIES:{symbol}:{timeframe}")
            last_by_series[series] = parsed
    return {
        "passed": not errors,
        "errors": errors,
        "records": len(records),
        "feature_definitions": len(definitions),
        "contract": CONTRACT_ID,
        "promotion_allowed": False,
    }
