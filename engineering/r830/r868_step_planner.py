"""Offline, deterministic STEP implementation planner; never executes code."""
import re

NAME = re.compile(r'^[a-z][a-z0-9_]{0,63}$')

def plan(payload):
    fail = {'status': 'blocked', 'executed': False, 'certified_e2e': False}
    if type(payload) is not dict or set(payload) != {'step_id', 'module', 'approved', 'paper_only'}:
        return {**fail, 'reason': 'invalid_payload'}
    step = payload['step_id']
    module = payload['module']
    if payload['paper_only'] is not True or payload['approved'] is not True:
        return {**fail, 'reason': 'approval_or_paper_required'}
    if type(step) is not int or not 1 <= step <= 100000 or type(module) is not str or not NAME.fullmatch(module):
        return {**fail, 'reason': 'invalid_step_or_module'}
    prefix = f'step_{step:05d}_{module}'
    return {'status': 'planned_only', 'agent_id': 'dev.step_planner_agent', 'step_id': step,
            'plan': [{'kind': 'implementation', 'path': f'engineering/steps/{prefix}.py'},
                     {'kind': 'unit_test', 'path': f'tests/test_{prefix}.py'},
                     {'kind': 'review', 'check': 'offline_regression_and_sha256'}],
            'executed': False, 'certified_e2e': False}
