# ET665 — Certificação offline por Git Blob — 2026-11-16

## Escopo
- Branch isolada: `engineering/et665-trader-wiring-failclosed-20261116`.
- `mind_trader/app/engines/core.py` — Git Blob `bb2eced75254e9dc7d81456eac6cba18260c4e25`.
- `tests/test_et665_legacy_jsonl_writer_safety.py` — Git Blob `b759da0a7f98b8ab6bb0f61ba3eb13e91fcc57b2`.
- Conteúdos reconstruídos localmente a partir da versão publicada, com `git hash-object` confirmando igualdade de bytes para os dois arquivos.

## Execução
```bash
python -m unittest discover -s tests -p 'test_et665_legacy_jsonl_writer_safety.py' -v
```

Resultado: **23 tests, 23 PASS, 0 FAIL**, execução offline, persistência exclusivamente em diretórios temporários.

## Controles
- Modo LIVE/UNKNOWN rejeitado; símbolo obrigatório; JSONL rejeita NaN/infinito/objetos inválidos.
- Cálculo de risco considera PnL negativo e exposição aberta; contadores exigem inteiros não negativos.
- Não executado em Docker nem em GitHub Actions; não é certificação E2E S19→S20→S21.
- MAIN e produção intactas; PAPER_ONLY; REAL_ORDERS e FTMO_REAL proibidos; R$0.

## Próxima lacuna
Localizar produtor CSV S20 e autoridade original de símbolo, sem backfill especulativo.
