from dataclasses import asdict, is_dataclass
import hashlib
import json
import time
from pathlib import Path


def _safe_hash(value) -> str:
    return hashlib.sha256(str(value or "").encode("utf-8", errors="ignore")).hexdigest()[:16]


def _safe_obj(value):
    try:
        if is_dataclass(value):
            return asdict(value)
        if isinstance(value, (str, int, float, bool, type(None), list, dict)):
            return value
        return str(value)
    except Exception:
        return str(value)


def record_selector_canary_diff(
    *,
    source: str,
    legacy_response,
    candidate,
    selected,
    final_path: str = "legacy_bridge_preserved",
):
    legacy_hash = _safe_hash(legacy_response)
    candidate_response = getattr(candidate, "response", "")
    candidate_hash = _safe_hash(candidate_response)
    selected_text = getattr(selected, "response", selected)
    selected_hash = _safe_hash(selected_text)

    diff = {
        "mission": "P4.95J10A2",
        "stage": "FORCE_CANARY_RECORD",
        "ts": time.time(),
        "source": source,
        "legacy_hash": legacy_hash,
        "candidate_hash": candidate_hash,
        "selected_hash": selected_hash,
        "candidate_matches_legacy": candidate_hash == legacy_hash,
        "selected_matches_legacy": selected_hash == legacy_hash,
        "selected_matches_candidate": selected_hash == candidate_hash,
        "final_path": final_path,
        "candidate": _safe_obj(candidate),
        "selected": _safe_obj(selected),
    }

    path = Path("_evidence/P4.95J9_SELECTOR_CANARY_DIFF/canary_diff.jsonl")
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(diff, ensure_ascii=False, default=str) + "\n")

    return diff
