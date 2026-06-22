# Repository Governance Lock

## Regras

- Nunca usar `git add .`
- Nunca usar `git commit -a`
- Nunca usar `git push --all`
- Nunca commitar `_evidence`, backups, runtime state, vídeos, zips, dumps ou patches temporários.
- Toda missão deve staged apenas arquivos explicitamente aprovados.
- Toda alteração de runtime exige:
  - backup
  - py_compile
  - import app
  - pytest focado
  - TestClient probe
  - git diff --cached --stat

## Runtime certificado

- P19P29 Universal Domain Context Scoping
- P19P30D Legacy Interceptor Containment

## Arquivos críticos

- app/main.py
- app/api/whatsapp.py
- app/context_runtime/universal_domain_context.py
- app/context_runtime/p19p28_context.py
- app/domains/universal_domain_router.py
- app/domains/fitness_runtime.py
- tests/test_p19p28k_contextual_fitness.py
- tests/test_p19p29_universal_domain_context.py
- tests/test_p19p30d_legacy_interceptor_containment.py
