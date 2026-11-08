# ET665.R89 — Lacuna de contabilização da sessão PAPER (2026-11-08)

## Evidência de código
- `products/eldora_trader/mind_trader/app/execution/gateway.py`: `submit_order` chama `self.paper.pre_trade_check(...)`, encaminha ao `paper_route_order` e registra ledger de execução, mas não chama `self.paper.record_trade_result`.
- `mind_trader/app/execution/paper_session.py`: `pre_trade_check` verifica `s["trades"] >= s["max_daily_trades"]` e limites de perda, mas não incrementa `trades`.
- Somente `record_trade_result(pnl)` incrementa `trades`, atualiza PnL e grava a sessão.

## Impacto e limites da conclusão
O fluxo inspecionado não prova que toda ordem PAPER aceita seja contabilizada antes de uma próxima ordem. Se o resultado não for registrado por outro componente, o limite de quantidade diária pode ser contornado por sucessivas submissões. Não se afirma que isso já ocorreu, nem que inexista um consumidor externo de resultados.

## Decisão
`SESSION_TRADE_COUNT_CERTIFIED=FALSE`; `PHASE_B=OPEN`. Não alterar produção sem contrato para momento de contabilização, semântica de fill versus fechamento, idempotência por `paper_order_id`, concorrência e rollback. Criar regressões isoladas que demonstrem a lacuna e uma proposta de correção, sem habilitar ordens reais.

`MAIN=UNTOUCHED | REAL_ORDERS=FORBIDDEN`
