from app.runtime.capability_usage_ledger import log_capability

def test_p474d_usage_ledger():

    row = log_capability(
        sender_id="p474d_test",
        capability="semantic_retrieval",
        success=True,
        latency_ms=12
    )

    assert row["capability"] == "semantic_retrieval"
    assert row["success"] is True
