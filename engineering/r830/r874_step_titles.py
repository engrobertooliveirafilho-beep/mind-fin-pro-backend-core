"""Extract historical STEP titles without granting implementation or certification status."""
import re

PATTERN = re.compile(r'^\s*STEP\s+(\d+)\s*[—–-]\s*(\S.*)\s*$', re.IGNORECASE)

def reconcile(step_ids, source_text):
    blocked = {'status': 'blocked', 'certified': 0, 'executed': 0}
    if type(step_ids) is not list or len(step_ids) > 10000 or any(type(s) is not int or s < 1 for s in step_ids):
        return {**blocked, 'reason': 'invalid_steps'}
    if type(source_text) is not str or len(source_text) > 2_000_000:
        return {**blocked, 'reason': 'invalid_source'}
    titles = {}
    conflicts = set()
    for line in source_text.splitlines():
        match = PATTERN.fullmatch(line)
        if match:
            number, title = int(match.group(1)), match.group(2).strip()
            if number in titles and titles[number] != title:
                conflicts.add(number)
            titles[number] = title
    requested = sorted(set(step_ids))
    return {'status': 'titles_only', 'defined': {str(s): titles[s] for s in requested if s in titles and s not in conflicts},
            'unresolved': [s for s in requested if s not in titles or s in conflicts],
            'conflicts': sorted(conflicts.intersection(requested)),
            'certified': 0, 'executed': 0, 'e2e_certified': False}
