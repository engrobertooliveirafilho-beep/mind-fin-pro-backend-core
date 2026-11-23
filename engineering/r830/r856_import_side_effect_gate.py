"""R856: conservative AST inspection for import-time side effects. No exec/import."""
import ast

BLOCKED_CALLS = {'start_scheduler', 'subprocess.run', 'shutil.copy', 'os.system', 'open', 'exec', 'eval'}
BLOCKED_METHODS = {'mkdir', 'write_text', 'write_bytes', 'copy', 'run', 'start'}

def inspect_import_safety(source):
    blocked = {'status': 'blocked', 'runtime_certified': False, 'execution_authorized': False}
    if not isinstance(source, bytes) or not source or len(source) > 2_000_000:
        return {**blocked, 'reason': 'invalid_source'}
    try:
        tree = ast.parse(source.decode('utf-8'))
    except (UnicodeDecodeError, SyntaxError, ValueError):
        return {**blocked, 'reason': 'invalid_python'}
    aliases = {}
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                aliases[alias.asname or alias.name] = alias.name
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                aliases[alias.asname or alias.name] = (node.module or '') + '.' + alias.name
    def name(expr):
        if isinstance(expr, ast.Name):
            return aliases.get(expr.id, expr.id)
        if isinstance(expr, ast.Attribute):
            return name(expr.value) + '.' + expr.attr
        return ''
    findings = set()
    def check(n):
        for child in ast.walk(n):
            if isinstance(child, ast.Call):
                nme = name(child.func)
                if nme in BLOCKED_CALLS or nme.split('.')[-1] in BLOCKED_METHODS or nme.split('.')[-1] == 'start_scheduler':
                    findings.add(nme)
                if nme in {'getattr', 'globals', 'locals', '__import__'}:
                    findings.add('dynamic_dispatch')
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            for decorator in node.decorator_list:
                check(decorator)
            for default in (node.args.defaults if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) else []):
                check(default)
        else:
            check(node)
    if findings:
        return {**blocked, 'reason': 'import_time_side_effect_risk', 'findings': sorted(findings)}
    return {'status': 'candidate_only', 'runtime_certified': False,
            'execution_authorized': False, 'reason': 'static_only_not_certified'}
