import json
from pathlib import Path


def test_p464d_memory_quarantine_manifest_exists_and_is_valid():
    path = Path("app/runtime/memory_quarantine_manifest.json")

    assert path.exists(), "memory_quarantine_manifest.json does not exist"

    data = json.loads(path.read_text(encoding="utf-8"))

    assert data["mission"] == "P4.64C_MEMORY_QUARANTINE_MANIFEST"
    assert data["policy"]["delete_files"] is False
    assert data["policy"]["quarantine_type"] == "logical_manifest_only"
    assert data["policy"]["orphaned_modules_policy"] == "do_not_integrate_without_explicit_revalidation"

    required = {
        "ACTIVE_IN_PIPELINE",
        "ACTIVE_IN_WHATSAPP_ADAPTER",
        "ACTIVE_OUTSIDE_PIPELINE",
        "ORPHANED_OR_UNUSED",
    }

    assert set(data["buckets"].keys()) == required
    assert set(data["counts"].keys()) == required

    for key in required:
        assert isinstance(data["buckets"][key], list)
        assert data["counts"][key] == len(data["buckets"][key])

    assert data["counts"]["ACTIVE_IN_PIPELINE"] >= 1
    assert data["counts"]["ORPHANED_OR_UNUSED"] >= 1


def test_p464d_orphaned_modules_are_not_treated_as_active():
    data = json.loads(Path("app/runtime/memory_quarantine_manifest.json").read_text(encoding="utf-8"))

    active = set(data["buckets"]["ACTIVE_IN_PIPELINE"])
    active |= set(data["buckets"]["ACTIVE_IN_WHATSAPP_ADAPTER"])
    active |= set(data["buckets"]["ACTIVE_OUTSIDE_PIPELINE"])

    orphaned = set(data["buckets"]["ORPHANED_OR_UNUSED"])

    assert active.isdisjoint(orphaned), "A module cannot be active and orphaned at the same time"

    known_orphans = {
        "app.runtime.memory_adapter",
        "app.runtime.semantic_dialogue_memory",
        "app.memory.longitudinal_memory",
    }

    assert known_orphans.intersection(orphaned), (
        "Expected at least one known orphaned memory module to remain quarantined"
    )
