# Dispatcher canonical — modo aninhado fail-closed

- Falha identificada: `{'context':{'mode':'live'}}` e `{'MODE':'real'}` não eram rejeitados no validador anterior.
- Correção: verificação recursiva e case-insensitive da chave `mode`, exigindo exclusivamente `dry_run`; aplicada à entrada e à resposta.
- Teste real offline: `python -m unittest discover -s tests -p test_agents_unified_runtime_recovery.py -v` → **22/22 PASS**, 0 falhas, 0.001s.
- Log SHA-256: `5784f8be34d9204bf2b18e46d82d3847ee4f79c781ccba6eac4334cd52456169`.
- Git blob do código testado: `1e4cdd66c705b5edf305b654fd4f7e702d24233c`.
- Git blob dos testes executados: `69caf1af90a9f4b6ae44f59d196253ff2fc3249d`.
- Evidência histórica PAPER broker no Drive: `1eo0JQ7CuxEEfiQoQTo5sJ6DWM5sa76I3`; não equivale a execução atual.
- Limite: testes unitários com agentes simulados; 5 fontes históricos recuperados são stubs; sem E2E.

`PAPER_ONLY=TRUE | REAL_ORDERS=FORBIDDEN | MAIN=INTACTA | E2E_CERTIFIED=FALSE | COST=R$0`
