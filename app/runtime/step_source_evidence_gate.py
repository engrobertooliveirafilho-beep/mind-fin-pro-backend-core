"""Fail-closed audit of recovered MIND STEP source; no dynamic execution."""
import ast

def inspect_step_source(step_id, source):
    if type(step_id) is not int or step_id <= 0 or not isinstance(source, str):
        raise ValueError('invalid STEP evidence')
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError) as exc:
        raise ValueError('invalid STEP Python source') from exc
    statuses = []
    declared_ids = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == 'STEP_STATUS':
                    statuses.append(node.value.value if isinstance(node.value, ast.Constant) else None)
                if isinstance(target, ast.Name) and target.id == 'STEP_ID':
                    declared_ids.append(node.value.value if isinstance(node.value, ast.Constant) else None)
    if len(declared_ids) != 1 or type(declared_ids[0]) is not int or declared_ids[0] != step_id:
        raise ValueError('STEP identity mismatch')
    if len(statuses) != 1 or statuses[0] != 'implemented':
        return {'step_id': step_id, 'source_status': 'NOT_IMPLEMENTED', 'certified': False}
    return {'step_id': step_id, 'source_status': 'IMPLEMENTATION_CLAIM', 'certified': False}
