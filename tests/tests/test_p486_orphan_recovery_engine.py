import json
from pathlib import Path

def test_p486_orphan_recovery_engine():
    orphan = json.loads(
        Path("runtime/orphan_recovery/orphan_recovery_plan.json").read_text(encoding="utf-8")
    )

    adapter = json.loads(
        Path("runtime/orphan_recovery/adapter_recovery_plan.json").read_text(encoding="utf-8")
    )

    assert orphan["milestone"] == "P4.86 COMPLETE"
    assert orphan["mode"] == "PLAN_ONLY"
    assert orphan["total_orphans"] == 15

    assert adapter["milestone"] == "P4.86 COMPLETE"
    assert adapter["mode"] == "PLAN_ONLY"
    assert adapter["total_adapters"] == 4

    for item in orphan["orphans"]:
        assert item["approval_required"] is True
        assert item["execution_blocked_by"] == "P4.83_GATE"

    for item in adapter["adapters"]:
        assert item["approval_required"] is True
        assert item["execution_blocked_by"] == "P4.83_GATE"
