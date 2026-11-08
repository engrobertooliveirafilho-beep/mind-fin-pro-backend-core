import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "app/p1525b_cloud_dataset_reconstruction_fix/engine.py"

def test_r241_certification_requires_independent_authority():
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    assignments = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "status" for t in node.targets)
    ]
    assert len(assignments) == 1
    assert isinstance(assignments[0].value, ast.Constant)
    assert assignments[0].value.value == "RESEARCH_ONLY"

def test_r241_no_direct_paper_certification_literal():
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    status_assignments = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "status"
            for target in node.targets
        )
    ]
    assert len(status_assignments) == 1
    assert isinstance(status_assignments[0].value, ast.Constant)
    assert status_assignments[0].value.value == "RESEARCH_ONLY"

def test_r241_real_order_forbidden():
    source = SOURCE.read_text(encoding="utf-8")
    tree = ast.parse(source)
    assert 'REAL_ORDERS' in source
    assert 'FORBIDDEN' in source
    assert not any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "order_send"
        for node in ast.walk(tree)
    )