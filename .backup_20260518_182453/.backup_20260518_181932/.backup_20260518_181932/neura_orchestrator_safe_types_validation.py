from app.orchestrator.prompt_orchestrator import PromptOrchestrator

o = PromptOrchestrator()

cases = [
    ("me explique derivadas", {}, {"facts": ["Roberto", "matemática"]}),
    ("oi", [], {"history": [{"role": "user", "message": "oi"}]}),
]

for msg, mem, ret in cases:
    ans = o.answer(msg, memory_context=mem, retrieved_context=ret)
    print("INPUT:", msg)
    print("OUTPUT:", ans)
    assert isinstance(ans, str)
    assert "WEBHOOK_ERROR" not in ans

print("ORCHESTRATOR_SAFE_TYPES_PASS")
