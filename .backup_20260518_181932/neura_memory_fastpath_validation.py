from app.orchestrator.prompt_orchestrator import PromptOrchestrator

o = PromptOrchestrator()
ctx = "Roberto está estudando matemática e tem prova sexta."

assert o.answer("qual meu nome?", memory_context=ctx) == "Seu nome é Roberto."
assert o.answer("o que estou estudando?", memory_context=ctx) == "Você está estudando matemática."
assert o.answer("quando é minha prova?", memory_context=ctx) == "Sua prova é sexta."
assert "Derivada" in o.answer("me explique derivadas", memory_context=ctx)

print("MEMORY_FASTPATH_AND_COGNITIVE_ORCHESTRATOR_PASS")
