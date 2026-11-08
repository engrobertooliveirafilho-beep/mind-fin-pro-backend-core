# ET665.R109 — Contrato mínimo de correlação PAPER (2026-11-08)

## Fonte inspecionada
- `products/eldora_trader/mind_trader/app/execution/paper_broker_adapter.py`: `write_paper_broker_ledger` gera `paper_order_id` por `uuid.uuid4()` no momento da gravação.
- `products/eldora_trader/mind_trader/app/execution/gateway.py`: `submit_order` não fornece `session_id`, `reservation_id` ou `order_id` estável ao broker PAPER.
- `mind_trader/tests/security_review/test_et665_r108_actual_broker_schema.py`: regressão estática e validação fail-closed adicionadas, CI a confirmar.

## Contrato para integração futura (NÃO implementado)
1. Atribuir identificador de ordem estável e `session_id` validado antes de reservar capacidade; preservar o mesmo identificador no broker e em todos os ledgers.
2. Reservar capacidade atomicamente **antes** do fill, sem liberar uma reserva ambígua após falha de escrita.
3. Gravar evento de preenchimento idempotente e reconciliar SQLite, ledger do broker, ledger do gateway e sessão por identificador.
4. Diferenciar contagem de operações preenchidas do PnL realizado no encerramento; não chamar `record_trade_result(0)` como substituto de liquidação.
5. Na ausência de correlação, em duplicidade, em crash/retry ou divergência de ledgers: bloquear novas ordens PAPER e exigir reconciliação explícita.
6. Proibir alteração de modos LIVE/FTMO_REAL e executar somente em branch isolada com testes offline e revisão independente.

## Estado
- A suíte R90 ainda reproduz aceitação repetida sem incremento de `trades` no gateway original.
- A suíte R108 identifica lacuna de vínculo; seus testes não são uma correção de produção.
- `PHASE_B=OPEN | SESSION_ACCOUNTING=FAIL | MAIN=UNTOUCHED | REAL_ORDERS=FORBIDDEN`
