"""Offline implementations of four recovered Dev agent contracts. No I/O or execution."""
import re

NAME = re.compile(r'^[a-z][a-z0-9_]{0,63}$')
AGENTS = ('dev.code_blueprint_agent', 'dev.test_guardian_agent', 'dev.refactor_assistant_agent', 'dev.impl_squad_coordinator')


def run_dry(agent_id, payload):
    blocked = {'status': 'blocked', 'executed': False, 'e2e_certified': False}
    if agent_id not in AGENTS or type(payload) is not dict or set(payload) != {'step_id', 'module', 'approved', 'paper_only'}:
        return {**blocked, 'reason': 'invalid_request'}
    step, module = payload['step_id'], payload['module']
    if payload['approved'] is not True or payload['paper_only'] is not True:
        return {**blocked, 'reason': 'approval_or_paper_required'}
    if type(step) is not int or not 1 <= step <= 100000 or type(module) is not str or not NAME.fullmatch(module):
        return {**blocked, 'reason': 'invalid_step_or_module'}
    stem = f'step_{step:05d}_{module}'
    implementation = f'engineering/steps/{stem}.py'
    test = f'tests/test_{stem}.py'
    if agent_id == AGENTS[0]:
        result = {'module': implementation, 'test': test, 'functions': ['validate_input', 'run_dry'], 'write_authorized': False}
    elif agent_id == AGENTS[1]:
        result = {'target': implementation, 'tests': [test], 'checks': ['input_validation', 'no_side_effects', 'regression', 'hash_attestation'], 'suite_executed': False}
    elif agent_id == AGENTS[2]:
        result = {'target': implementation, 'changes': ['isolate_side_effects', 'add_input_guards', 'preserve_contract'], 'patch_applied': False}
    else:
        result = {'backlog': [{'agent': a, 'step_id': step, 'module': module} for a in AGENTS[:3]], 'dispatched': False}
    return {'status': 'planned_only', 'agent_id': agent_id, 'step_id': step, 'result': result, 'executed': False, 'e2e_certified': False}
