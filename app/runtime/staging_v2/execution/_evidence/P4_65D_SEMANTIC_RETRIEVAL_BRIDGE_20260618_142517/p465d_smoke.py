import traceback
from app.runtime.cognitive_pipeline import run_cognitive_pipeline

cases = [
    "Use retrieval da base do Drive para responder: qual é o estado atual da Eldora?",
    "Com base nos documentos ingeridos do Drive, qual capability deve ser integrada agora?",
    "Procure no grafo de conhecimento módulos órfãos e diga o próximo passo.",
]

print("P4.65D_SMOKE_START")

for msg in cases:
    print("\n" + "=" * 90)
    print("INPUT:", msg)
    try:
        out = run_cognitive_pipeline("p465d_semantic_bridge", msg)
        print("TYPE:", type(out).__name__)
        print("ANSWER:", str(out.get("answer") if isinstance(out, dict) else out)[:2500])
        if isinstance(out, dict):
            print("INTENT:", out.get("intent"))
            print("STATE:", out.get("state"))
    except Exception:
        print("ERROR")
        print(traceback.format_exc())

print("\nP4.65D_SMOKE_COMPLETE")
