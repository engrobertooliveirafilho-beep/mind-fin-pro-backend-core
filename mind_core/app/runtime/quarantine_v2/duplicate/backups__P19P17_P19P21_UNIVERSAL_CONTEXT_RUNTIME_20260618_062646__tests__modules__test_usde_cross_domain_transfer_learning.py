from app.modules.usde_core.cross_domain_transfer_learning import CrossDomainTransferLearning

def test_transfer():
    r=CrossDomainTransferLearning().transfer(
        "lottery",
        "finance",
        ["entropy","markov","graph"]
    )

    assert r["transfer_score"] > 0

def test_recommend():
    r=CrossDomainTransferLearning().recommend([
        {"domain":"finance","score":0.8},
        {"domain":"lottery","score":0.6}
    ])

    assert r["recommended"]=="finance"
