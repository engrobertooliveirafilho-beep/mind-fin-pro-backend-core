from app.knowledge_lifecycle import KnowledgeLifecycleManager


def test_step532_create_and_get_latest_active():
    mgr = KnowledgeLifecycleManager()
    item1 = mgr.create("canon:mind:estrategia", {"text": "v1"})
    item2 = mgr.revise("canon:mind:estrategia", {"text": "v2"})

    latest = mgr.get_latest_active("canon:mind:estrategia")
    assert latest is not None
    assert latest.version == item2.version
    assert latest.payload["text"] == "v2"
    assert item1.status == "active"


def test_step532_deprecate_makes_item_inactive():
    mgr = KnowledgeLifecycleManager()
    item1 = mgr.create("canon:mind:riscos", {"text": "versao unica"})
    mgr.deprecate("canon:mind:riscos", version=item1.version)

    latest = mgr.get_latest_active("canon:mind:riscos")
    assert latest is None
    assert item1.status == "deprecated"

