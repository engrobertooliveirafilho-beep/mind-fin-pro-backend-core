"""Explicit, inert offline scheduler replacement for historical auto-hook.

No threads, file I/O, imports of historical runtimes, or agent execution.
"""
import re

_ID = re.compile(r'[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*\Z')
MAX_AGENTS = 100


def plan_tick(registry, *, dry_run=True):
    blocked = {'status': 'blocked', 'executed': 0, 'runtime_certified': False,
               'integration_authorized': False}
    if dry_run is not True:
        return {**blocked, 'reason': 'offline_only'}
    if type(registry) is not dict or set(registry) != {'agents'} or type(registry['agents']) is not list:
        return {**blocked, 'reason': 'invalid_registry'}
    agents = registry['agents']
    if len(agents) > MAX_AGENTS:
        return {**blocked, 'reason': 'batch_limit'}
    selected, seen = [], set()
    for agent in agents:
        if type(agent) is not dict or set(agent) != {'id', 'governance'}:
            return {**blocked, 'reason': 'invalid_agent'}
        ident, governance = agent['id'], agent['governance']
        if type(ident) is not str or not _ID.fullmatch(ident) or ident in seen:
            return {**blocked, 'reason': 'invalid_agent_id'}
        if type(governance) is not dict or set(governance) != {'auto_run'} or type(governance['auto_run']) is not bool:
            return {**blocked, 'reason': 'invalid_governance'}
        seen.add(ident)
        if governance['auto_run']:
            selected.append(ident)
    return {'status': 'planned', 'agent_ids': selected, 'executed': 0,
            'runtime_certified': False, 'integration_authorized': False}


def start_scheduler(*args, **kwargs):
    """Legacy-compatible entrypoint: never starts a background worker."""
    return {'status': 'blocked', 'reason': 'autonomous_scheduler_disabled',
            'executed': 0, 'runtime_certified': False, 'integration_authorized': False}
