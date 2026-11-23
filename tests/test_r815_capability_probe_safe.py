"""R815 regression: no module imports or calls during default capability inspection."""
import importlib.util
from pathlib import Path
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / "app" / "runtime" / "capability_recovery_bridge.py"
spec = importlib.util.spec_from_file_location("r815_bridge_under_test", SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_default_never_imports_or_executes():
    with patch.object(module.importlib, "import_module", side_effect=AssertionError("unexpected import")):
        report = module.capability_recovery_report()
    assert report["mode"] == "static_safe"
    assert report["summary"]["total"] == len(module.TOP5_MODULES)
    assert report["summary"]["with_successful_calls"] == 0
    assert report["summary"]["skipped_active_probes"] == len(module.TOP5_MODULES)
    assert all(x["skipped"] and not x["import_ok"] and x["call_results"] == {} for x in report["modules"])


def test_false_opt_in_stays_safe():
    with patch.object(module.importlib, "import_module", side_effect=AssertionError("unexpected import")):
        report = module.capability_recovery_report(execute_probes=False)
    assert report["mode"] == "static_safe"


def test_truthy_nonboolean_opt_in_stays_safe():
    with patch.object(module.importlib, "import_module", side_effect=AssertionError("unexpected import")):
        report = module.capability_recovery_report(execute_probes=1)
    assert report["mode"] == "static_safe"


def test_user_message_preserved_without_import():
    with patch.object(module.importlib, "import_module", side_effect=AssertionError("unexpected import")):
        report = module.capability_recovery_report(user_id="u", message="m")
    assert report["user_id"] == "u"
    assert report["message"] == "m"


def test_explicit_opt_in_uses_legacy_path_with_mocked_modules():
    class FakeModule:
        pass
    with patch.object(module, "inspect_capability_module", return_value={
        "module": "fake", "import_ok": False, "functions": [], "classes": [],
        "call_results": {}, "error": "blocked_mock",
    }) as inspect_mock:
        report = module.capability_recovery_report(execute_probes=True)
    assert "mode" not in report
    assert inspect_mock.call_count == len(module.TOP5_MODULES)
    assert report["summary"]["with_successful_calls"] == 0
