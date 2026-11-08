# ET665.R91 — Reprodução confirmada da lacuna PAPER (2026-11-08)

- Commit testado: `cde1dc4c2e678540e8535abbaab49cf2139f1eb9`.
- GitHub Actions: https://github.com/engrobertooliveirafilho-beep/mind-fin-pro-backend-core/actions/runs/42480041977 — `completed/success`.
- Evidência: artefato `13617320912`, 2369 bytes, SHA-256 ZIP `719231c4384a1cb0353ab07475ddc3b18a072b82130842f28f65d1fc6ca0d231`.
- Seis suítes fixadas: R69, R77, R82, R84, R86 e R90.
- R90 é um **teste de reprodução de vulnerabilidade**, não um teste de proteção: confirma que, com `max_daily_trades=1` e `trades=0`, duas submissões PAPER passam e geram duas aceitações sem incrementar o contador da sessão.
- Componentes originais do gateway, broker, preenchimento e precheck da sessão são extraídos via AST, sem imports de conectividade; risco, FTMO e adversarial permanecem dublês. Não se comprova ocorrência real nem fluxo de produção.
- Gate de contabilização de sessão: `FAIL/NOT_CERTIFIED`, apesar do CI `PASS`. Correção exige contrato para reserva/commit de trade, idempotência por identificador de ordem, atomicidade e concorrência, evitando contabilizar rejeições.
- Workflow R338 falha separadamente. Nenhuma mudança em main ou autorização de ordem real.

`PHASE_B=OPEN | REGRESSION=PASS | SESSION_ACCOUNTING=FAIL | MAIN=UNTOUCHED | REAL_ORDERS=FORBIDDEN`
