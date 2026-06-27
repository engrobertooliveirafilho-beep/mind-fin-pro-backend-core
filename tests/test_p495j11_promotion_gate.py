import json

from app.runtime.final_authority_promotion_gate import evaluate_final_authority_promotion


def test_p495j11_gate_approves_clean_sample(tmp_path):
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

    decision = evaluate_final_authority_promotion(str(p))

    assert decision.approved is True
    assert decision.reason == "PROMOTION_APPROVED_FOR_CONTROLLED_CANARY"
    assert decision.metrics["error_rate"] == 0.0


def test_p495j11_gate_blocks_low_sample(tmp_path):
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
    p.write_text("\n".join(json.dumps(row) for _ in range(9)), encoding="utf-8")

    decision = evaluate_final_authority_promotion(str(p))

    assert decision.approved is False
    assert decision.reason == "INSUFFICIENT_SAMPLES"


def test_p495j11_gate_blocks_error_record(tmp_path):
    p = tmp_path / "canary_diff.jsonl"
    p.write_text(json.dumps({"error": "boom"}) + "\n", encoding="utf-8")

    decision = evaluate_final_authority_promotion(str(p))

    assert decision.approved is False
