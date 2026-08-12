from __future__ import annotations

import ast
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from statistics import mean


TARGET_MODULES = [f"P{i}" for i in range(1871, 1901)]

FORBIDDEN_LIVE_TERMS = [
    "ORDER_SENT" + " = true",
    "REAL_ORDERS" + " = true",
    "FTMO_REAL" + " = true",
    "MT5_REAL" + " = true",
    "send_order(",
    "order_send(",
    "live=True",
    "mode='LIVE'",
    'mode="LIVE"',
]

PROXY_TERMS = [
    "placeholder",
    "mock",
    "synthetic",
    "dummy",
    "fake",
    "todo",
    "pass",
    "random",
    "sample",
    "heuristic",
    "hardcoded",
]

BIAS_TERMS = [
    "future",
    "shift(-",
    "lookahead",
    "leakage",
    "target leakage",
    "survivorship",
]

INSTITUTIONAL_TERMS = [
    "walk_forward",
    "monte_carlo",
    "stress",
    "regime",
    "black_swan",
    "out_of_sample",
    "purged",
    "embargo",
    "cross_validation",
    "drawdown",
    "correlation",
    "exposure",
    "causal",
    "counterfactual",
    "feature_importance",
    "decay",
    "confidence_interval",
]


@dataclass
class ModuleAudit:
    module: str
    files: int
    lines: int
    functions: int
    classes: int
    proxy_hits: int
    bias_hits: int
    institutional_hits: int
    safety_violations: int
    depth_score: float
    classification: str
    gaps: list[str]


def classify(score: float) -> str:
    if score < 20:
        return "TOY"
    if score < 40:
        return "PROTOTYPE"
    if score < 60:
        return "INTERMEDIATE"
    if score < 75:
        return "ADVANCED"
    if score < 90:
        return "INSTITUTIONAL"
    return "STATE_OF_THE_ART"


def scan_python_file(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()

    try:
        tree = ast.parse(text)
        functions = sum(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) for n in ast.walk(tree))
        classes = sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree))
    except Exception:
        functions = 0
        classes = 0

    lower = text.lower()

    return {
        "lines": len(lines),
        "functions": functions,
        "classes": classes,
        "proxy_hits": sum(lower.count(t.lower()) for t in PROXY_TERMS),
        "bias_hits": sum(lower.count(t.lower()) for t in BIAS_TERMS),
        "institutional_hits": sum(lower.count(t.lower()) for t in INSTITUTIONAL_TERMS),
        "safety_violations": sum(text.count(t) for t in FORBIDDEN_LIVE_TERMS),
    }


def score_module(metrics: dict) -> tuple[float, list[str]]:
    gaps = []

    code_depth = min(metrics["lines"] / 1000, 1.0) * 20
    structure_depth = min((metrics["functions"] + metrics["classes"] * 2) / 60, 1.0) * 20
    institutional_depth = min(metrics["institutional_hits"] / 40, 1.0) * 30

    proxy_penalty = min(metrics["proxy_hits"] * 2, 20)
    bias_penalty = min(metrics["bias_hits"] * 3, 20)
    safety_penalty = 100 if metrics["safety_violations"] > 0 else 0

    score = code_depth + structure_depth + institutional_depth + 30
    score -= proxy_penalty
    score -= bias_penalty
    score -= safety_penalty

    score = max(0, min(100, score))

    if metrics["lines"] < 500:
        gaps.append("LOW_CODE_DENSITY")
    if metrics["institutional_hits"] < 10:
        gaps.append("LOW_INSTITUTIONAL_SIGNAL")
    if metrics["proxy_hits"] > 0:
        gaps.append("PROXY_OR_PLACEHOLDER_RISK")
    if metrics["bias_hits"] > 0:
        gaps.append("BIAS_OR_LEAKAGE_RISK")
    if metrics["safety_violations"] > 0:
        gaps.append("SAFETY_LOCK_VIOLATION")

    return round(score, 2), gaps


# P1901_SINGLE_PASS_PYTHON_INDEX
def build_python_index(repo: Path) -> list[Path]:
    """Enumerate Python files once for the complete institutional audit."""
    return list(repo.rglob("*.py"))


def discover_module_files(index: list[Path], module: str) -> list[Path]:
    module_token = module.lower()

    return [
        path
        for path in index
        if module_token in str(path).lower()
        or module_token in path.name.lower()
    ]
def audit(repo: Path) -> dict:
    reports = []


    python_index = build_python_index(repo)
    for module in TARGET_MODULES:
        files = discover_module_files(python_index, module)

        metrics = {
            "lines": 0,
            "functions": 0,
            "classes": 0,
            "proxy_hits": 0,
            "bias_hits": 0,
            "institutional_hits": 0,
            "safety_violations": 0,
        }

        for file in files:
            scanned = scan_python_file(file)
            for key in metrics:
                metrics[key] += scanned[key]

        score, gaps = score_module(metrics)

        reports.append(ModuleAudit(
            module=module,
            files=len(files),
            lines=metrics["lines"],
            functions=metrics["functions"],
            classes=metrics["classes"],
            proxy_hits=metrics["proxy_hits"],
            bias_hits=metrics["bias_hits"],
            institutional_hits=metrics["institutional_hits"],
            safety_violations=metrics["safety_violations"],
            depth_score=score,
            classification=classify(score),
            gaps=gaps,
        ))

    institutional_score = round(mean([r.depth_score for r in reports]), 2)

    return {
        "program": "P1901_DEPTH_AUDIT",
        "mode": "RESEARCH_ONLY",
        "order_sent": False,
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
        "mt5_real": "FORBIDDEN",
        "institutional_readiness_score": institutional_score,
        "modules": [asdict(r) for r in reports],
        "gap_ranking": sorted(
            [asdict(r) for r in reports],
            key=lambda x: (x["depth_score"], -len(x["gaps"]))
        ),
        "priority_queue": [
            {
                "module": r.module,
                "action": "DEEPEN_EXISTING_MODULE",
                "reason": r.gaps,
                "target": "INSTITUTIONAL_DEPTH"
            }
            for r in sorted(reports, key=lambda x: x.depth_score)
            if r.depth_score < 75 or r.gaps
        ],
    }


if __name__ == "__main__":
    repo = Path.cwd()
    result = audit(repo)

    out = Path("_evidence") / "P1901_DEPTH_AUDIT_REPORT.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps({
        "status": "PASS",
        "program": "P1901_DEPTH_AUDIT",
        "mode": "RESEARCH_ONLY",
        "institutional_readiness_score": result["institutional_readiness_score"],
        "report": str(out),
        "order_sent": False,
        "real_orders": "FORBIDDEN"
    }, indent=2))
