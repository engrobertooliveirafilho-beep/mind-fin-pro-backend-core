from app.eldora.core.neura_scale_runtime import (
    create_tenant,
    create_whatsapp_acquisition_campaign,
    schedule_cognition_workload,
    activate_public_launch
)

def test_tenant():
    assert create_tenant("default")["status"]=="ok"

def test_whatsapp_acquisition():
    assert create_whatsapp_acquisition_campaign("students","free_trial")["status"]=="ok"

def test_cost_scheduler():
    assert schedule_cognition_workload("retrieval",0.5,20)["status"]=="ok"

def test_public_launch():
    assert activate_public_launch("NEURA","students")["status"]=="ok"

