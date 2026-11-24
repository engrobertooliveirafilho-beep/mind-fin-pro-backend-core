import ast
import math
import operator
from app.tools.registry import register_tool

OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv}

def evaluate(node):
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        result = float(node.value)
    elif isinstance(node, ast.BinOp) and type(node.op) in OPS:
        result = OPS[type(node.op)](evaluate(node.left), evaluate(node.right))
    elif isinstance(node, ast.UnaryOp) and type(node.op) in (ast.UAdd, ast.USub):
        result = evaluate(node.operand) * (-1 if isinstance(node.op, ast.USub) else 1)
    else:
        raise ValueError('Unsupported expression')
    if not math.isfinite(result):
        raise ValueError('Nonfinite result')
    return result

@register_tool('calc')
def tool_calc(expr):
    try:
        if not isinstance(expr, str) or len(expr) > 256:
            raise ValueError('Invalid expression')
        return {'ok': True, 'result': evaluate(ast.parse(expr, mode='eval').body)}
    except (ValueError, SyntaxError, ArithmeticError, RecursionError):
        return {'ok': False, 'error': 'Invalid arithmetic expression'}
