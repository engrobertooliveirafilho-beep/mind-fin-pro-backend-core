from app.orchestrator.prompt_orchestrator import PromptOrchestrator

o=PromptOrchestrator()

ctx={
    "facts":{"name":"Roberto","study":"matemática","exam":"sexta"},
    "history_text":"Meu nome é Roberto.\nEstou estudando matemática.\nMinha prova é sexta."
}

print(o.answer(
    "qual meu nome?",
    memory_context=ctx.get("history_text",""),
    retrieved_context=ctx
))

print(o.answer(
    "o que estou estudando?",
    memory_context=ctx.get("history_text",""),
    retrieved_context=ctx
))

print(o.answer(
    "quando é minha prova?",
    memory_context=ctx.get("history_text",""),
    retrieved_context=ctx
))
