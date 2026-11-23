"""Fail-closed P2403B provenance check. OHLC input does not prove strategy replay."""
import ast
from pathlib import Path

def inspect_replay_builder(path):
    tree=ast.parse(Path(path).read_text(encoding="utf-8"))
    names={n.id for n in ast.walk(tree) if isinstance(n,ast.Name)}
    uses_hash='hashlib' in names and any(isinstance(n,ast.Attribute) and n.attr=='sha256' for n in ast.walk(tree))
    has_strategy_signal=any(isinstance(n,ast.FunctionDef) and n.name in ('evaluate_strategy_signal','replay_strategy_signals') for n in ast.walk(tree))
    return {'hash_seeded_sampling':uses_hash,'strategy_signals_verified':has_strategy_signal,
            'correlation_research_ready':False,'strategy_performance_certified':False,
            'runtime_promotion_allowed':False}
