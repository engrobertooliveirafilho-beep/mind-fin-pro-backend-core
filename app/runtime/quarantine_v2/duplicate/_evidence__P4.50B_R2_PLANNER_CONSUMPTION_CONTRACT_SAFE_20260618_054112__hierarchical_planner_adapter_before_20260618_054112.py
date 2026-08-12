from app.p7_adapters.hierarchical_contracts import (
    HierarchicalPlanRequest,
    HierarchicalPlanResponse,
    HierarchyNode,
)

def plan_hierarchy(req: HierarchicalPlanRequest) -> HierarchicalPlanResponse:
    root = HierarchyNode(
        node_id="root",
        title=req.goal,
        objective=req.user_intent,
        status="planned",
        children=[],
    )

    return HierarchicalPlanResponse(
        root_goal=req.goal,
        nodes=[root],
        execution_order=["root"],
        next_action="shadow_plan_ready",
        audit_trace=["p7_adapter", "no_runtime_mutation"],
    )

def plan(goal=None, context=None):
    req = HierarchicalPlanRequest(
        user_intent=str(goal or ""),
        goal=str(goal or ""),
        context=context or {},
    )
    return plan_hierarchy(req).model_dump()
