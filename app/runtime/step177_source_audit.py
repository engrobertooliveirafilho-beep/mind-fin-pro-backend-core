"""Read-only source audit; route presence is not STEP functionality."""
import ast

def audit_step177(source: str) -> dict:
    if not isinstance(source, str):
        raise ValueError('source must be text')
    try:
        tree=ast.parse(source)
    except SyntaxError as exc:
        raise ValueError('invalid Python source') from exc
    functions=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name=='run_step_177']
    if len(functions)!=1:
        raise ValueError('expected one run_step_177')
    fn=functions[0]
    if len(fn.body)==1 and isinstance(fn.body[0],ast.Return):
        try:
            payload=ast.literal_eval(fn.body[0].value)
        except (ValueError,TypeError,OverflowError):
            payload=None
        if isinstance(payload,dict) and payload.get('step')==177 and payload.get('status')=='active':
            return {'step_id':177,'kind':'STATIC_METADATA_ENDPOINT','certified':False}
    return {'step_id':177,'kind':'UNVERIFIED_IMPLEMENTATION','certified':False}
