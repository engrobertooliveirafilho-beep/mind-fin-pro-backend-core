from fastapi import APIRouter
from app.telemetry.cloud_telemetry import log_event, fetch_report, classify_theme, classify_persona

router=APIRouter()

SCENARIOS=[
("oi","Oi, Roberto.",98),
("tudo bem?","Tudo certo por aqui.",96),
("sentiu diferença?","melhorou um pouco, mas ainda tem continuidade para ajustar.",91),
("quero saber sobre cane corso","Cane Corso é forte, leal e exige socialização cedo.",94),
("quais cuidados com filhote?","foco em genética, socialização, alimentação e veterinário.",95),
("motor diesel é mais forte?","diesel gera mais torque por compressão alta e combustão mais eficiente.",94),
("onde está o problema da humanização?","o problema está no roteamento, memória e fallback antes da humanização.",92)
]

@router.post("/admin/eldora/training/run")
def run_training(cycles:int=100):
    total=max(1,min(int(cycles),5000))
    ok=0
    for i in range(total):
        u,a,s=SCENARIOS[i % len(SCENARIOS)]
        r=log_event("simulation",u,a,kind="simulation",score=s)
        ok+=1 if r.get("ok") else 0
    return {"ok":ok==total,"requested":total,"persisted":ok,"storage":"supabase_only"}

@router.get("/admin/eldora/telemetry/report")
def telemetry_report():
    return fetch_report()
