from app.eldora.core.real_world_action_engine import execute_action
from app.eldora.core.universal_tool_controller import register_tool
from app.eldora.core.environment_execution_engine import execute_workflow

def test_tool_registration():
    r=register_tool("gmail","email_automation")
    assert r["status"]=="ok"

def test_action_execution():
    r=execute_action("gmail","send_email")
    assert r["status"]=="ok"

def test_workflow_execution():
    r=execute_workflow("lead_followup","crm_environment")
    assert r["status"]=="ok"
