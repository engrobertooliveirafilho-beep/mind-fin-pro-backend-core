import traceback
from app.runtime.cognitive_pipeline import run_cognitive_pipeline

cases = [
    "Use o knowledge graph para responder: qual é o próximo passo do MIND?",
    "Use retrieval da base do Drive para responder: qual é o estado atual da Eldora?",
    "Com base nos documentos ingeridos do Drive, qual capability deve ser integrada agora?",
    "Procure no grafo de conhecimento módulos órfãos e diga o próximo passo.",
]

print("P4.65A_RUNTIME_CONSUMPTION_PROBE")

for msg in cases:
    print("\n" + "=" * 90)
    print("INPUT:", msg)
    try:
        out = run_cognitive_pipeline("p465a_drive_kg_probe", msg)
        print("TYPE:", type(out).__name__)
        print("VALUE:", str(out)[:5000])
    except Exception:
        print("ERROR:")
        print(traceback.format_exc())

print("\nP4.65A_PROBE_COMPLETE")
