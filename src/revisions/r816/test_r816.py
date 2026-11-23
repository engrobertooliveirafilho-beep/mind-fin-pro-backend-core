import ast
import importlib.util
from pathlib import Path
from unittest.mock import patch

SOURCE = Path(__file__).with_name('capability_recovery_bridge.py')
spec = importlib.util.spec_from_file_location('r816_capability_bridge', SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_default_passive():
    r = module.capability_recovery_report()
    assert r['mode'] == 'declared_only'
    assert r['summary']['total'] == 5
    assert r['summary']['functionally_certified'] == 0


def test_true_opt_in_blocked():
    r = module.capability_recovery_report(execute_probes=True)
    assert r['active_probe_requested'] is True
    assert r['active_probe_allowed'] is False
    assert r['summary']['with_successful_calls'] == 0


def test_nonboolean_opt_in_blocked():
    assert module.capability_recovery_report(execute_probes=1)['active_probe_requested'] is False


def test_no_import_module_calls():
    with patch('importlib.import_module', side_effect=AssertionError('import attempted')):
        module.capability_recovery_report(execute_probes=True)
        module.capability_recovery_report()


def test_static_no_dynamic_imports_or_calls():
    tree = ast.parse(SOURCE.read_text())
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)]
    assert not any(isinstance(n.func, ast.Attribute) and n.func.attr in ('import_module', 'exec', 'eval') for n in calls)
    assert not any(isinstance(n.func, ast.Name) and n.func.id in ('__import__', 'eval', 'exec') for n in calls)


def test_all_five_declared():
    r = module.capability_recovery_report()
    assert [x['module'] for x in r['modules']] == list(module.TOP5_MODULES)


def test_no_false_positive():
    r = module.capability_recovery_report(execute_probes=True)
    assert all(not x['import_ok'] and x['certification'] == 'not_tested' for x in r['modules'])


def test_no_functions_or_classes_executed():
    r = module.capability_recovery_report(execute_probes=True)
    assert all(not x['functions'] and not x['classes'] and not x['call_results'] for x in r['modules'])


def test_metadata_preserved():
    r = module.capability_recovery_report('user', 'message')
    assert (r['user_id'], r['message']) == ('user', 'message')


def test_falsy_none_still_safe():
    assert module.capability_recovery_report(execute_probes=None)['active_probe_allowed'] is False
