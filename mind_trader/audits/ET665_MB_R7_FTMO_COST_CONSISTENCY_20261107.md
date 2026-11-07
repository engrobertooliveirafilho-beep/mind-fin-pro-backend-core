# ET665.MB.R7 — Consistência de custos FTMO e fill PAPER

Data: 2026-11-07. Revisão direta dos contratos no GitHub; não foram executados testes ou operações de corretora.

## Defeito confirmado por inspeção
`simulate_fill` (R6) rejeita spread/slippage/commission negativos, mas `validate_ftmo_config` (R3) ainda validava custos negativos. Isso permitia classificar uma configuração como válida e somente rejeitar a ordem na camada de fill, gerando divergência entre decisões.

## Correção publicada
- Commit `c1487df521ebe08672120f1ecbbe3a46478c9c6a`: regras FTMO rejeitam custos negativos e `max_position_size` não positivo; zero continua permitido para custos.
- Commit `d5fdb6de546a075d10be6b6bba8db3ef44dd6eb9`: **7 casos** de regressão preparados (3 custos negativos, 2 tamanhos de posição, 1 default válido, 1 leitura de config inválida). **NÃO EXECUTADOS**.

## Risco residual
- `paper_broker_adapter` ainda persiste `order` completo no ledger local; sanitização necessária antes de qualquer publicação.
- A verificação dos 74 pontos do inventário permanece parcial.
- 50/50 PASS anteriores não cobrem R2–R7. R2–R6: 157 casos novos; R7: 7; **164 casos preparados sem execução**.
- Independent review waived by owner, not equivalent to approval.

`R7_PATCH=STAGED_UNTESTED`
`R7_TESTS=7_PREPARED_NOT_EXECUTED`
`PHASE_B=OPEN`
`REAL_ORDERS=FORBIDDEN`
`FTMO_REAL=FORBIDDEN`
`MAIN_MERGE=BLOCKED`
