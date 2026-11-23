"""Static fail-closed P2403E source provenance gate."""
import ast
from pathlib import Path
def certify(source):
    tree=ast.parse(Path(source).read_text(encoding="utf-8"))
    hashed=any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=="sha256" for n in ast.walk(tree))
    return {"hash_sampled":hashed,"strategy_replay_certified":False,
            "portfolio_correlation_certified":False,"runtime_promotion_allowed":False}
