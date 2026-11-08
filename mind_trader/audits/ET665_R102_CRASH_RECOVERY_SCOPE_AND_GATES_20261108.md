# ET665.R102 — Limites de certificação de crash recovery (2026-11-08)

## Evidência já disponível
- O teste R101 usa processo Python filho e `os._exit` antes ou depois de `COMMIT`, sobre SQLite local temporário.
- O CI da versão `5e21d726` terminou `success` (execução ainda anterior à inclusão de R101 no runner).
- O CI da versão `89dc06a4`, que fixa dez suítes incluindo R101, requer resultado próprio antes de declarar PASS.

## Limites
- Testa encerramento abrupto de processo, **não** falha de energia, corrupção de disco, disco cheio, isolamento multiprocesso em ambiente Windows ou consistência entre SQLite e ledger JSONL.
- SQLite do R95 é protótipo exclusivamente de teste; gateway original continua sem reserva atômica e contabilização de fill integrada.
- R90 demonstra que duas ordens PAPER podem ser aceitas com limite diário de uma operação no fluxo isolado original.

## Próximos gates
1. Confirmar run e hashes da versão com dez suítes.
2. Testar concorrência multiprocesso, transição de reserva e reconciliação do ledger.
3. Projetar integração transacional com risco/FTMO, preservar semântica de PnL no fechamento e exigir revisão independente antes de qualquer alteração de execução.

`PHASE_B=OPEN | SESSION_ACCOUNTING=FAIL | MAIN=UNTOUCHED | REAL_ORDERS=FORBIDDEN`
