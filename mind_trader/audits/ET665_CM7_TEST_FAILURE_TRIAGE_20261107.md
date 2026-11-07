# ET665.CM.7 — Correção após execução local

Operador executou 15 testes: 12 PASS, 3 FAIL (exit code 1). Falhas exclusivamente em `test_report_staging_replaces_remote_upload` para P15.16, P15.25B e P15.6–P15.10. Causa: teste rejeitava toda ocorrência de `REMOTE_NORM`, incluindo uso permitido como origem de leitura no comando `rclone copy "gdrive:..." "local"`.

Correção publicada no teste: proibir `REMOTE_REPORTS` e exigir `REMOTE_NORM` como primeira interpolação de caminho remoto no comando de leitura. A função de execução continua protegida por `cmd/run_cmd` com `shell=False`, `check=True` e destino remoto proibido. Nenhuma alteração adicional nos motores.

**Estado:** patch publicado; reexecução necessária. Não declarar 15/15 PASS antes de JUnit. Não executar suíte histórica nem alterar Drive histórico.

CM7_PREVIOUS=12_PASS_3_FAIL
CM7_PATCH=PUBLISHED
CM7_RETEST=PENDING
PHASE_B=OPEN
REAL_ORDERS=FORBIDDEN
FTMO_REAL=FORBIDDEN
