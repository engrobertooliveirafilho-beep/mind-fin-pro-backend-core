# ET665.CM.4 — Reconciliação de execução local (evidência reportada)
Data: 2026-11-07
Branch: audit/et665h-paper-ci-security-review-20261106
Workflow CI configurado: commit 28daa2c69672ac1e22ac82c05370a52a081ae38f.

## Fonte da evidência
Saída PowerShell fornecida pelo operador na conversa, após checkout seletivo do clone GitHub e criação de venv Python 3.12.
- pytest 9.2.0 instalado.
- Saída: `.......... [100%]`.
- `ET665.CM3_EXIT_CODE=0`.
- Diretório local reportado: `D:\MIND_T~1\SYSTEM~1\ET665_CM3_ISOLATED`.
- Escopo: `mind_trader/tests/test_et665_cm2_residual_guards.py` (10 testes).
- JUnit, log e arquivo de SHA-256 foram solicitados no comando, mas seus conteúdos/bytes não foram transmitidos ao conector. HASH_VERIFICATION=NOT_POSSIBLE_YET; ARTIFACT_UPLOAD=NOT_DONE.

## Reconciliação com matriz
- Quatro rotas P15: 8 testes PASS reportados para execução rclone com shell=False/check=True, bloqueio de escrita e guarda de limpeza.
- P77B/P79: 2 testes AST PASS reportados para bloqueio inicial.
- P77 e demais rotas MT5 independentes: PENDING.
- Destino de exportação governado fora do Drive histórico: PENDING.
- Persistência no Drive ledger: NOT_EXECUTED.
- CI remota: NO_CONFIRMED_RUN; suíte histórica 99/99 NÃO reexecutada.
- Esses 10 testes não constituem prova de segurança integral nem validação FTMO.

## Gate
LOCAL_REGRESSION=10/10_OPERATOR_REPORTED_PASS
HASH_VERIFICATION=PENDING
JUNIT_LOG_UPLOAD=PENDING
PHASE_B=OPEN
SECURITY_APPROVAL=NOT_GRANTED
REAL_ORDERS=FORBIDDEN
FTMO_REAL=FORBIDDEN
NO_MAIN_MERGE
