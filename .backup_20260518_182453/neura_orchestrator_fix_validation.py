import json
from app.orchestrator.prompt_orchestrator import PromptOrchestrator

o = PromptOrchestrator()
tests = {
    "me explique derivadas": "Derivada",
    "oi": "Oi",
    "resuma este conteúdo": "resumo",
}

results=[]
ok=True
for msg, expected in tests.items():
    ans=o.run(msg)
    passed=expected.lower() in ans.lower() and "Informação registrada" not in ans
    ok = ok and passed
    results.append({"message":msg,"expected_contains":expected,"response":ans,"pass":passed})

print(json.dumps({"all_pass":ok,"results":results},ensure_ascii=False,indent=2))
raise SystemExit(0 if ok else 1)
