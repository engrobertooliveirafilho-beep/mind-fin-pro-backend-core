from datetime import datetime, timezone
import uuid

DYNAMIC_SKILLS = {}

def generate_skill(skill_name:str, domain:str):
    skill_id = str(uuid.uuid4())

    skill = {
        "skill_id":skill_id,
        "skill_name":skill_name,
        "domain":domain,
        "runtime_ready":True,
        "created_at":datetime.now(timezone.utc).isoformat()
    }

    DYNAMIC_SKILLS[skill_id] = skill

    return {
        "status":"ok",
        "skill":skill,
        "skills_total":len(DYNAMIC_SKILLS)
    }

def skill_report():
    return {
        "status":"ok",
        "skills_total":len(DYNAMIC_SKILLS),
        "skills":list(DYNAMIC_SKILLS.values())[-50:]
    }
