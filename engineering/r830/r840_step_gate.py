"""R840: fail-closed, offline step provenance gate. No runtime imports."""
import re
from pathlib import PurePosixPath

STATUS = {'CANDIDATE', 'VERIFIED_SOURCE', 'BLOCKED'}

def classify(path):
    if not isinstance(path, str) or not path or '\x00' in path:
        return 'INVALID'
    path = path.replace('\\', '/')
    if path.startswith('/') or re.match(r'^[A-Za-z]:', path) or any(p in ('', '.', '..') for p in path.split('/')):
        return 'INVALID'
    if re.search(r'(^|/)steps/step[^/]+\.(py|md|txt|json)$', path, re.I):
        return 'COGNITIVE_CANDIDATE'
    return 'UNCLASSIFIED'

def validate(entries, evidence=None):
    if not isinstance(entries, list) or not entries:
        return {'valid': False, 'errors': ['empty_registry'], 'certified': False}
    evidence = evidence if isinstance(evidence, dict) else {}
    ids, paths, errors = set(), set(), []
    for i, e in enumerate(entries):
        if not isinstance(e, dict) or set(e) != {'id','path_canonical','status','source_bucket_prefix'}:
            errors.append(f'{i}:schema'); continue
        ident, path, status, bucket = (e[k] for k in ('id','path_canonical','status','source_bucket_prefix'))
        if not all(isinstance(x, str) and x.strip() for x in (ident,path,status,bucket)):
            errors.append(f'{i}:empty'); continue
        if ident in ids or path in paths:
            errors.append(f'{i}:duplicate')
        ids.add(ident); paths.add(path)
        if classify(path) == 'INVALID': errors.append(f'{i}:path')
        if status not in STATUS: errors.append(f'{i}:status')
        if status == 'VERIFIED_SOURCE' and not re.fullmatch('[a-f0-9]{64}', evidence.get(path, '')):
            errors.append(f'{i}:missing_sha256')
    return {'valid': not errors, 'errors': errors, 'certified': False, 'count': len(entries)}
