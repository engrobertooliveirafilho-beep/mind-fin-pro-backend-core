# ET665.CM.5 — Pendências para transição B → C
Data: 2026-11-07

## Aplicado na branch isolada
- Fail-closed explícito nos entrypoints P77, P13.8 (mt5_probe), P13.9 (pull), P1505B, P1804, P1805 (discovery), P76A, P76A2 e P76B.
- Mantidos os bloqueios anteriores P77B/P79.
- Teste estrutural novo: mind_trader/tests/test_et665_cm5_mt5_fail_closed.py (9 casos parametrizados), ainda NÃO EXECUTADO.
- Não houve execução de MT5, ordem, rclone, nem suíte histórica nesta publicação.

## Decisão de exportação
- Drive histórico continua SOMENTE LEITURA. Não foi concedida permissão para upload rclone dos motores P15.
- GitHub é o destino governado de código, relatórios e evidências; artefatos de execução devem ser validados e publicados em branch de auditoria com hashes, sem promoção automática ou credenciais.
- O fluxo de exportação automática P15 permanece BLOQUEADO até implementação/teste de adaptador explícito de publicação. Não alegar EXPORT_READY.

## Gaps remanescentes
- Executar 9 regressões CM5 offline e publicar JUnit, log e SHA-256.
- Confirmar por inspeção/execução isolada que todos os entrypoints relevantes do escopo estão protegidos; escopo global não inventariado integralmente.
- Revisar efeitos colaterais de importação e garantir que o bloqueio não compromete caminhos de leitura offline desejados.
- Implementar e testar destino governado de exportação sem escrita no Drive histórico.
- Atualizar ledger do Drive com evidências e emitir parecer formal de segurança.

PHASE_B=OPEN
SECURITY_APPROVAL=NOT_GRANTED
REAL_ORDERS=FORBIDDEN
FTMO_REAL=FORBIDDEN
NO_MAIN_MERGE
