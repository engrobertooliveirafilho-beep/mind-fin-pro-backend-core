"""Static, fail-closed audit of recovered Python agent candidates."""
import ast
import hashlib

BAD_STATUSES = frozenset({'stub', 'not_implemented', 'todo', 'placeholder'})

def audit_agent_source(source, expected_sha256):
    if not isinstance(source, bytes) or not source or len(source) > 2_000_000:
        return {'status': 'blocked', 'reason': 'invalid_source'}
    if not isinstance(expected_sha256, str) or len(expected_sha256) != 64:
        return {'status': 'blocked', 'reason': 'invalid_digest'}
    if hashlib.sha256(source).hexdigest() != expected_sha256:
        return {'status': 'blocked', 'reason': 'digest_mismatch'}
    try:
        tree = ast.parse(source.decode('utf-8'))
    except (UnicodeDecodeError, SyntaxError, ValueError):
        return {'status': 'blocked', 'reason': 'invalid_python'}
    functions = {node.name for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    if 'run_dry' not in functions and 'run' not in functions:
        return {'status': 'blocked', 'reason': 'no_entrypoint'}
    literals = {node.value.lower() for node in ast.walk(tree) if isinstance(node, ast.Constant) and isinstance(node.value, str)}
    markers = sorted(BAD_STATUSES & literals)
    if markers:
        return {'status': 'blocked', 'reason': 'stub_markers', 'markers': markers}
    return {'status': 'candidate_only', 'reason': 'static_inspection_not_functional_proof', 'runtime_certified': False}
