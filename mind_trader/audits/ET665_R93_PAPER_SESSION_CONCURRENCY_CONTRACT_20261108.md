# ET665.R93 — Contrato pendente de contabilização concorrente (2026-11-08)

## Inspeção
- `paper_session.py` realiza `_read_session` + mutação + `_write_session` em `record_trade_result`, sem lock, transação ou compare-and-swap explícitos no método inspecionado.
- `pre_trade_check` apenas lê o contador `trades`; não reserva capacidade. `gateway.py` não chama `record_trade_result` após aceitar o preenchimento PAPER.
- `record_trade_result(pnl)` não recebe `paper_order_id` ou chave idempotente, logo não demonstra prevenção de duplicatas.

## Contrato proposto — não implementado
1. Reserva atômica de capacidade por sessão e identificador estável de ordem antes da aceitação; concorrência com limite 1 deve permitir no máximo uma reserva.
2. Commit idempotente do fill por `paper_order_id`; rejeição libera reserva sem incrementar contador.
3. Persistência recuperável após interrupção, sem contagem duplicada; atualização do PnL somente com evento de resultado explicitamente definido.
4. Regressões offline: corrida de duas submissões, duplicação, rejeição, crash/retry e fechamento da sessão.

## Status
O teste R90 reproduz a lacuna no fluxo isolado. R92 caracteriza somente a API sequencial existente; sua execução CI deve ser confirmada separadamente. Não afirmar que esta proposta é correção implementada.

`PHASE_B=OPEN | SESSION_ACCOUNTING=FAIL | CONCURRENCY=NOT_CERTIFIED | MAIN=UNTOUCHED | REAL_ORDERS=FORBIDDEN`
