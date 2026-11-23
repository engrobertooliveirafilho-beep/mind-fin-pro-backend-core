"""P2401 offline evidence provenance gate; no runtime imports or order execution."""
import ast
from pathlib import Path

def classify_source(path):
    tree=ast.parse(Path(path).read_text(encoding='utf-8'))
    names={n.name for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
    stable_calls=any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='stable_float' for n in ast.walk(tree))
    historical_read=any(isinstance(n,ast.Constant) and isinstance(n.value,str) and any(t in n.value.lower() for t in ('mt5_deals','historical_trades','market_bars','ohlcv')) for n in ast.walk(tree))
    return {'synthetic_metrics': 'stable_float' in names and stable_calls, 'historical_market_data_evidenced':historical_read,
            'runtime_promotion_allowed': False, 'performance_certified':False}
