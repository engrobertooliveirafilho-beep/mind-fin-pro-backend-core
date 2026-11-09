# ET665.MB.R11 — FTMO rule audit fail-closed

Data: 2026-11-07. Inspeção do código e publicação GitHub. Não houve execução pytest, corretora, rede, Drive histórico ou merge.

## Achado
`audit_rule_application` assumia que `trade` e `config` eram mappings válidos, fazia aritmética sem validação e podia lançar exceções ou persistir o payload completo. Isso enfraquecia a rastreabilidade e a rejeição determinística de entradas adversariais.

## Correção
- `71f7b0d68176f2042d45720385dab61d464647bc`: validação fail-closed de tipos, campos numéricos, limites e overflow; relatório sem payload bruto da operação.
- `ad568ac4eb61a46654cc63dea17fa6ca2c50f9ee`: 23 casos de regressão preparados (5 tipos, 15 campos, 1 overflow, 1 controle positivo, 1 privacidade). Não executados.
- `a7d76c642cd9b1cbc8087ada60457ff5195522d7`: executor consolidado atualizado para **250 testes** esperados (50 históricos + 200 novos).

## Limites
A aceitação simulada exige a execução conjunta offline, prova JUnit, ZIP/SHA-256 e revisão das rotas residuais. O runner não impõe isolamento de rede no sistema operacional. Revisão independente foi dispensada pelo proprietário, não certificada.

`R11_PATCH=PUBLISHED_UNTESTED`
`CONSOLIDATED_EXPECTED=250`
`CONSOLIDATED_EXECUTION=PENDING`
`PHASE_B=OPEN`
`REAL_ORDERS=FORBIDDEN`
`FTMO_REAL=FORBIDDEN`
`MAIN_MERGE=BLOCKED`
