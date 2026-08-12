import asyncio
import importlib
import inspect
import json
from pathlib import Path

SRC = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\MIND-GRAPH-9_CORE_RUNTIME_PROMOTION_PLAN_20260625_221136\\mind_graph_9_core_runtime_promotion_plan.json")

FORBIDDEN_PRODUCTION = [
    "production_allowed",
    "real_execution",
    "real_order",
    "live_order",
    "direct_user_response",
]

def _load_plan():
    data = json.loads(SRC.read_text(encoding="utf-8"))
    return data["promotion_plan"]

def _public_zero_arg_functions(module):
    out = []
    for name, fn in inspect.getmembers(module, inspect.isfunction):
        if name.startswith("_"):
            continue
        if fn.__module__ != module.__name__:
            continue
        sig = inspect.signature(fn)
        required = [
            p for p in sig.parameters.values()
            if p.default is inspect._empty
            and p.kind in (
                p.POSITIONAL_ONLY,
                p.POSITIONAL_OR_KEYWORD,
                p.KEYWORD_ONLY,
            )
        ]
        if not required:
            out.append((name, fn))
    return out

def _safe_assert_output(result):
    assert result is not None
    assert isinstance(result, (dict, list, str, int, float, bool))

    if isinstance(result, dict):
        assert any(k in result for k in [
            "status",
            "allowed",
            "state",
            "runtime_status",
            "tenant_id",
            "user_id",
            "graph",
            "tasks",
            "plans",
            "checkpoint_id",
        ])

        dumped = json.dumps(result, ensure_ascii=False).lower()
        for bad in FORBIDDEN_PRODUCTION:
            assert bad not in dumped

def test_mind_graph_10_source_has_5_core_candidates():
    plan = _load_plan()
    assert len(plan) == 5
    assert all(p["allowed_mode"] == "SHADOW_ONLY" for p in plan)
    assert all(p["production_allowed"] is False for p in plan)

def test_mind_graph_10_core_modules_import_and_contract_execute():
    plan = _load_plan()
    executed = []

    for p in plan:
        module = importlib.import_module(p["module"])
        funcs = _public_zero_arg_functions(module)

        assert funcs, f"No zero-arg public functions for {p['module']}"

        for name, fn in funcs:
            lname = name.lower()
            if any(x in lname for x in [
                "delete", "remove", "send", "post", "publish",
                "execute", "run", "write", "insert", "update",
                "real_order", "live_order", "worker_loop"
            ]):
                continue

            if inspect.iscoroutinefunction(fn):
                result = asyncio.run(asyncio.wait_for(fn(), timeout=3))
            else:
                result = fn()

            if inspect.iscoroutine(result):
                result.close()
                continue

            _safe_assert_output(result)
            executed.append(f"{p['module']}::{name}")

    assert len(executed) >= 5
