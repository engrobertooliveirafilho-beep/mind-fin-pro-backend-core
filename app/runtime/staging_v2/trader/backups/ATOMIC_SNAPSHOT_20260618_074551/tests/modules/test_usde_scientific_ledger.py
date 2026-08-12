from app.modules.usde_core.scientific_ledger import ScientificLedger

def test_scientific_ledger():
    ledger=ScientificLedger()

    ledger.append(
        "runtime_boot",
        {"status":"ONLINE"}
    )

    assert ledger.count() >= 1
