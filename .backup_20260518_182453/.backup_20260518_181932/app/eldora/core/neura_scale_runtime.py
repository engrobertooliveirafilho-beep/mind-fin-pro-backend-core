import uuid
from datetime import datetime, timezone

TENANTS=[]
ACQUISITION=[]
SCHEDULING=[]
LAUNCH=[]

def create_tenant(name:str, plan:str="starter"):
    item={
        "tenant_id":str(uuid.uuid4()),
        "name":name,
        "plan":plan,
        "status":"active",
        "created_at":datetime.now(timezone.utc).isoformat()
    }
    TENANTS.append(item)
    return {"status":"ok","tenant":item,"tenants_total":len(TENANTS)}

def create_whatsapp_acquisition_campaign(audience:str, offer:str):
    item={
        "campaign_id":str(uuid.uuid4()),
        "channel":"whatsapp",
        "audience":audience,
        "offer":offer,
        "status":"running",
        "created_at":datetime.now(timezone.utc).isoformat()
    }
    ACQUISITION.append(item)
    return {"status":"ok","campaign":item,"campaigns_total":len(ACQUISITION)}

def schedule_cognition_workload(workload:str, max_cost:float=1.0, priority:int=10):
    item={
        "schedule_id":str(uuid.uuid4()),
        "workload":workload,
        "max_cost":max_cost,
        "priority":priority,
        "routing":"cost_aware",
        "status":"scheduled",
        "created_at":datetime.now(timezone.utc).isoformat()
    }
    SCHEDULING.append(item)
    return {"status":"ok","schedule":item,"schedules_total":len(SCHEDULING)}

def activate_public_launch(product:str="NEURA", market:str="students"):
    item={
        "launch_id":str(uuid.uuid4()),
        "product":product,
        "market":market,
        "status":"public_launch_active",
        "created_at":datetime.now(timezone.utc).isoformat()
    }
    LAUNCH.append(item)
    return {"status":"ok","launch":item,"launches_total":len(LAUNCH)}

def neura_scale_report():
    return {
        "status":"ok",
        "tenants_total":len(TENANTS),
        "acquisition_campaigns_total":len(ACQUISITION),
        "schedules_total":len(SCHEDULING),
        "launches_total":len(LAUNCH),
        "tenants":TENANTS[-20:],
        "campaigns":ACQUISITION[-20:],
        "launches":LAUNCH[-20:]
    }
