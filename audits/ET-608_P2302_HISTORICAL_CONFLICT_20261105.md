# ET-608 — 2026-11-05 — Evidência P2302 original: conflito não arbitrado

## Fonte histórica inédita confrontada com PR #2
- Drive: pasta `P2302_PAPER_FORWARD_LOOP_20260622_123941` (`1A_nqdNpr0l98LwqrtfdYdcHgmkAdpbL6`).
- `paper_signal_ledger.csv` (Drive `18XdGtCpAhp-tS385Tp02Ya5Puf5tKxlq`): quatro candidatos para GER40/H1/20260622_11_H1, dois BUY e dois SELL, lote 0.01 cada; identificadores preservados nos testes.
- `summary.json` (Drive `1pV7qWmJzxJItmRglTivuNfD25d5yhlw6`): `total_candidate_signals=4`, `max_signal_candle=1`, `selected_action=BUY`, `selected_signal_id=P2302_5ed23464b49d`, `selected_lot=0.01`, `status=COMPLETE`; contém `mt5_order_file` e `order_line` locais (históricos). **Não prova envio de ordem.**
- `audit.json` e `paper_forward_state.json` permanecem artefatos adicionais, não certificados nesta auditoria.
- GitHub PR #2 head `ee2e5cbf8f4f5fca35cdedef2fcb6f1c5478de17` é draft. P2354 retorna `False` de conflito quando `candidate_signals` falta; teste legado atual autoriza esse caso.
- P2362 só chama P2354 após targeting; P2361 calcula sizing sem aplicar diretamente `precheck.lot_multiplier`. Assim, **não há certificação integrada nem autoridade para liberar emissão**.

## Escopo desta branch
- Regressão histórica independente em `audits/p2302_historical_conflict_detector.py` + `tests/test_p2302_historical_conflict_et608.py`: prova do caso conflitante e bloqueio simulado, sem uso de MT5, sem modificar a lógica operacional.
- Não constitui integração P2302/P2354/P2362, nem execução de CI. Execução de pytest deve ser comprovada por log separado antes de certificar.
- Drive histórico somente leitura. Ledger ET-608 pendente de atualização caso Google Docs esteja indisponível.
- Bloqueios: `PAPER_ONLY`, `REAL_ORDERS=FORBIDDEN`, `FTMO_REAL=FORBIDDEN`, PR #2 draft, `main` intocada, sem merge.
