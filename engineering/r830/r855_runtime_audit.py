"""R855: inspect historical runtime Python without importing or executing it."""
import ast

DANGEROUS = {'subprocess.run', 'shutil.copy', 'start_scheduler', 'mkdir', 'write_text'}

def audit_runtime(source):
    blocked = {'status': 'blocked', 'execution_authorized': False, 'runtime_certified': False}
    if not isinstance(source, bytes) or not source or len(source) > 2_000_000:
        return {**blocked, 'reason': 'invalid_source'}
    try:
        tree = ast.parse(source.decode('utf-8'))
    except (SyntaxError, UnicodeDecodeError, ValueError):
        return {**blocked, 'reason': 'invalid_python'}
    findings = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        if isinstance(fn, ast.Name):
            name = fn.id
        elif isinstance(fn, ast.Attribute):
            name = fn.attr
            if isinstance(fn.value, ast.Name):
                name = fn.value.id + '.' + name
        else:
            continue
        if name in DANGEROUS or name.split('.')[-1] in {'mkdir', 'write_text'}:
            findings.add(name)
    if findings:
        return {**blocked, 'reason': 'side_effect_calls', 'findings': sorted(findings)}
    return {'status': 'candidate_only', 'execution_authorized': False,
            'runtime_certified': False, 'reason': 'static_review_only'}
