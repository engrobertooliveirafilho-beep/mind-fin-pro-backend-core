from app.modules.usde_core.scientific_knowledge_sync import ScientificKnowledgeSync

def test_scientific_knowledge_sync():
    r=ScientificKnowledgeSync().sync(
        "H1",
        "E1",
        "EV1",
        "D1"
    )

    assert r["status"]=="SYNCED"
    assert r["summary"]["nodes"]==4
