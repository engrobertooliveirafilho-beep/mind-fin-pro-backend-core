"""Evidence classification only; historical labels never authorize execution."""
import re

SHA256 = re.compile(r'^[0-9a-f]{64}$')


def classify(step_id, registry_ids, titles, evidence):
    blocked = {'status': 'blocked', 'certified': False, 'execution_authorized': False}
    if type(step_id) is not int or step_id < 1 or type(registry_ids) is not list or type(titles) is not dict or type(evidence) is not dict:
        return {**blocked, 'reason': 'invalid_input'}
    if len(registry_ids) > 100000 or any(type(n) is not int or n < 1 for n in registry_ids):
        return {**blocked, 'reason': 'invalid_registry_ids'}
    if step_id not in registry_ids:
        return {**blocked, 'reason': 'not_in_registry'}
    title = titles.get(str(step_id))
    if type(title) is not str or not title.strip():
        return {'status': 'identifier_only', 'certified': False, 'execution_authorized': False}
    # A claim of SHA-256 is not proof of matching source or a passing test run.
    digest = evidence.get('sha256')
    if digest is not None and (type(digest) is not str or not SHA256.fullmatch(digest)):
        return {**blocked, 'reason': 'invalid_digest'}
    return {'status': 'definition_recovered', 'step_id': step_id, 'title': title,
            'has_unverified_digest': digest is not None,
            'certified': False, 'execution_authorized': False}
