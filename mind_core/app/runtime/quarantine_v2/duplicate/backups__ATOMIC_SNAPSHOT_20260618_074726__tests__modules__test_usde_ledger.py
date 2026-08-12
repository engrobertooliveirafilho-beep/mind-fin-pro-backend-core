from app.modules.usde_core.ledger import HypothesisLedger

def test_hypothesis_ledger_append():
    l = HypothesisLedger("_evidence/P4.46X_USDE_CORE/test_ledger")
    r = l.append(
        hypothesis="Toda hipótese nasce falsa",
        dataset_ref="synthetic://smoke",
        decision={"decision":"INCONCLUSIVA"},
        params={"seed":42}
    )
    assert "hash" in r
    assert len(l.all()) >= 1
