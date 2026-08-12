import json
import requests
import os
from app.mind.p5_5z_executive_snapshot.snapshot import ExecutiveSnapshot

u=os.getenv("SUPABASE_URL").rstrip("/")
k=os.getenv("SUPABASE_SERVICE_ROLE_KEY")

h={
    "apikey":k,
    "Authorization":"Bearer "+k
}

ev=requests.get(
    f"{u}/rest/v1/p55a_valuation_events?select=id,animal_id,amount,raw_payload&event_type=eq.P5.6E1_GENETIC_PRODUCTION_SCORE&order=amount.desc",
    headers=h
).json()

result={
    "genetic_score_events":len(ev),
    "top_scores":ev[:10],
    "snapshot":ExecutiveSnapshot().build()
}

print(json.dumps(result,indent=2,ensure_ascii=False,default=str))
