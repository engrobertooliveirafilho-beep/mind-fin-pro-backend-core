import json
from pathlib import Path

from app.runtime.final_authority_divergence_analyzer import analyze_canary_diff


def test_p495j10_divergence_analyzer_accepts_equivalent_records(tmp_path):
    p = tmp_path / "canary_diff.jsonl"
    row = {
        "source": "eldoraprimaryruntimereply",
        "legacy_hash": "abc",
        "candidate_hash": "abc",
        "selected_hash": "abc",
        "candidate_matches_legacy": True,
        "selected_matches_legacy": True,
        "selected_matches_candidate": True,
    }

    p.write_text("\n".join(json.dumps(row) for _ in range(10)), encoding="utf-8")

    result = analyze_canary_diff(str(p))

    assert result["ok"] is True
    assert result["total"] == 10
    assert result["equivalence_rate"] == 1.0
    assert result["promotion_ready"] is True


def test_p495j10_divergence_analyzer_blocks_critical_errors(tmp_path):
    p = tmp_path / "canary_diff.jsonl"
    p.write_text(json.dumps({"error": "boom"}) + "\n", encoding="utf-8")

    result = analyze_canary_diff(str(p))

    assert result["ok"] is True
    assert result["promotion_ready"] is False
    assert result["severity_count"]["CRITICAL"] == 1
