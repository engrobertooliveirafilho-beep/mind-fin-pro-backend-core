from app.orchestrator.prompt_orchestrator import PromptOrchestrator
o=PromptOrchestrator()
ctx={"facts":{"name":"Roberto","study":"matemática","exam":"sexta"},"history_text":""}
assert "Roberto" in o.answer("qual meu nome?", retrieved_context=ctx)
assert "matemática" in o.answer("o que estou estudando?", retrieved_context=ctx)
assert "sexta" in o.answer("quando é minha prova?", retrieved_context=ctx)
print("FACTS_FASTPATH_PASS")
