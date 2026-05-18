from fastapi import APIRouter

from app.eldora.core.real_world_action_engine import (
    execute_action,
    action_report
)

from app.eldora.core.universal_tool_controller import (
    register_tool,
    tool_report
)

from app.eldora.core.environment_execution_engine import (
    execute_workflow,
    workflow_report
)

router = APIRouter(
    prefix="/eldora/action",
    tags=["eldora-action"]
)

@router.post("/tool/register")
async def tool(tool_name:str, capability:str):
    return register_tool(tool_name, capability)

@router.get("/tool/report")
async def tools():
    return tool_report()

@router.post("/execute")
async def execute(tool:str, action:str):
    return execute_action(tool, action)

@router.get("/execute/report")
async def executions():
    return action_report()

@router.post("/workflow/run")
async def workflow(workflow:str, environment:str):
    return execute_workflow(workflow, environment)

@router.get("/workflow/report")
async def workflows():
    return workflow_report()
