# ET-608 — Execução isolada reproduzível — 2026-11-05

- Branch: `audit/p2302-historical-conflict-et608-20261105`
- Código: `audits/p2302_historical_conflict_detector.py`
- Testes: `tests/test_p2302_historical_conflict_et608.py`
- Execução: sandbox temporário, Python pytest, sem acesso MT5, sem credenciais ou ordens.
- Comando: `PYTHONPATH=. pytest -q -p no:cacheprovider tests/test_p2302_historical_conflict_et608.py`
- Resultado observado: `.... [100%]` / `4 passed in 0.06s`.
- Escopo: valida apenas detector histórico isolado e quatro cenários, **não** o código operacional integrado.
- CI GitHub não confirmada; `main` inalterada; nenhum merge.
- Governança: `PAPER_ONLY`, `REAL_ORDERS=FORBIDDEN`, `FTMO_REAL=FORBIDDEN`.
