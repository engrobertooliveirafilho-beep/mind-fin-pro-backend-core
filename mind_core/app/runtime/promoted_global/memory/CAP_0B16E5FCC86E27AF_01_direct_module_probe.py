from app.domains.fitness_runtime import is_fitness, reply
from app.context_runtime.p19p28_context import bind, get

print("FITNESS_IMPORT_OK", is_fitness("quero emagrecer"))
bind("+TESTE", "fitness", "quero emagrecer")
print("CTX", get("+TESTE"))
print(reply("quais"))
