# ET665.CM — Matriz de riscos residuais (PARCIAL)
Data: 2026-11-07
Fonte: ledger ET-701–ET-704; dossiês ET665; inspeção autenticada GitHub no commit 2f433010240f5d4cff5aa0c07082c70d0d47703d.

STATUS: INCOMPLETE / PHASE_B=OPEN / SECURITY_APPROVAL=NOT_GRANTED.
REAL_ORDERS=FORBIDDEN; FTMO_REAL=FORBIDDEN. Não fazer merge em main.

| Rota | Evidência direta | Risco residual | Decisão |
|---|---|---|---|
| mind_trader/app/execution/gateway.py | Modo PAPER/REPLAY/MICRO_SIM; LIVE bloqueado; fill PAPER obrigatório | Outros entrypoints não passam necessariamente pelo gateway | APROVADO SOMENTE NO ESCOPO |
| reports/P78_DEMO_ORDER_SEND_SINGLE_CONTROLLED/p78_demo_order_send.py | Sem import MetaTrader5 ou order_send; retorna P78_BLOCKED_INSTITUTIONAL | Nenhum envio observado nesta implementação | BLOQUEADO NA ORIGEM; 4/4 testes reportados PASS |
| reports/P77_DEMO_ORDER_CHECK_ONLY/p77_order_check_only.py | mt5.initialize, account_info, terminal_info, symbol_select, order_check; não há order_send no arquivo | Entrada independente e dependência de servidor DEMO/terminal; falta isolamento comprovado | PENDENTE; NÃO EXECUTAR |
| reports/P79_DEMO_ORDER_AUDIT_POSITION_MONITOR/p79_monitor.py | mt5.initialize, account_info, terminal_info, positions_get; não há order_send no arquivo | Conexão MT5 sem verificação prévia DEMO; exposição a conta real e dados de posições | PENDENTE; NÃO EXECUTAR |
| P138/P139, P1505, P1804/P1805, P76A/P76A2/P76B/P77B | Citados no inventário ET665.CJ/CK; conteúdo não inspecionado integralmente nesta etapa | Classificação semântica incompleta | PENDENTE |
| P15.16, P15.25B, P15.3–P15.5, P15.6–P15.10 | Ledger informa subprocess.run(shell=True) com comandos rclone por string | Origem de argumentos, injeção, escopo de escrita e falhas não comprovados | PENDENTE; NÃO EXECUTAR |
| P16.21D | Inspeção histórica relata import subprocess sem chamada | Revalidar escopo/entrypoint | PENDENTE DOCUMENTAL |
| institutional_healthcheck.py | Execução subprocess.run para testes, conforme ledger | Confirmar argumentos e isolamento | PENDENTE DOCUMENTAL |

## Evidências e restrições
- ET665.CL: 99/99 PASS conforme saída do operador, não reexecutados aqui.
- JUnit, logs e SHA-256 locais não acessados nesta execução; CLOUD_PERSISTENCE_GATE=NOT_EXECUTED.
- Preservar alterações locais P8.46_ftmo_rule_audit.json e P8.92_institutional_live_lock.json.
- Inventário CJ: 276 Python, 684 matches, 137 ocorrências prioritárias em 23 arquivos; correspondências não equivalem a vulnerabilidades.
- Nenhum patch aplicado: as duas rotas examinadas P77/P79 não contêm envio de ordem comprovado; o isolamento insuficiente requer decisão e testes focados antes de mudança.

## Gate de encerramento
1. Inspecionar arquivos restantes da fila CJ e mapear entrypoints, importações e efeitos.
2. Identificar gaps concretos e aplicar bloqueio fail-closed mínimo quando necessário.
3. Testar deltas em ambiente offline com mocks de MT5/subprocess e evidências JUnit/hash.
4. Reconciliar relatórios locais; publicar commits e hashes; atualizar ledger com resultado verificável.
5. Emitir parecer formal. Até lá PHASE_B=OPEN e nenhuma operação real autorizada.


## ET665.CM.1 — Classificação semântica dos caminhos identificados (2026-11-07)

Inspeção de código-fonte autenticada na branch de auditoria, sem inicializar MT5, rclone ou pytest. Escopo: arquivos canônicos mind_trader/app e mind_trader/reports; não inclui clones promoted/staging. A árvore recursiva global retornou truncated=true, portanto isto NÃO é inventário global exaustivo.

### MT5 — chamadas e decisão
| Componente | Efeito MT5 observado | Classificação | Controle pendente |
|---|---|---|---|
| P13.8 app/p138_platform_connectors/engine.py | initialize, terminal_info, shutdown | TERMINAL_DIAGNOSTIC; sem envio | conexão pode abrir terminal real; isolamento de ambiente |
| P13.9 app/p139_mt5_historical_data_puller/engine.py | initialize(path=MT5_PATH), symbol_select, copy_rates_from_pos, shutdown | MARKET_DATA_READ; sem envio | validar path, conta e destino dos CSVs |
| P1505b reports/P1505_DATA_INGESTION_ENGINE/p1505b_mt5_harvester.py | initialize, terminal/account_info, symbol_select, copy_rates_from_pos | MARKET_DATA_READ; sem envio | checagem de conta e isolamento |
| P1804 reports/P1804_REAL_MT5_HISTORY_DOWNLOAD_PROBE/p1804_real_mt5_history_download_probe.py | initialize, copy_rates_range, shutdown | MARKET_DATA_READ; sem envio | origem terminal/conta; nome REAL não prova negociação |
| P1805 reports/P1805_SYMBOL_DISCOVERY_AND_10Y_NORMALIZATION/p1805_symbol_discovery_10y_normalization.py | initialize, symbols_get, shutdown | SYMBOL_METADATA_READ; sem envio | isolamento de terminal |
| P76A reports/P76A_MT5_CONNECTION_AUDIT/p76a_mt5_connection_audit.py | initialize, account_info, terminal_info, shutdown | ACCOUNT_DIAGNOSTIC; sem envio | acesso e possível persistência de metadados de conta |
| P76A2 reports/P76A2_MT5_DEMO_VALIDATION_FIX/p76a2_demo_validation_fix.py | initialize, account_info, terminal_info, shutdown | DEMO_VALIDATION; sem envio | validação ocorre após conexão |
| P76B reports/P76B_MT5_DEMO_ENVIRONMENT_CERTIFICATION/p76b_certify_environment.py | initialize, account_info, terminal_info, symbol_info/tick, symbol_select, shutdown | DEMO_ENV_DIAGNOSTIC; sem envio | isolamento terminal e checagens |
| P77 reports/P77_DEMO_ORDER_CHECK_ONLY/p77_order_check_only.py | initialize, symbol_select, order_check; request TRADE_ACTION_DEAL | ORDER_PRECHECK; NÃO ENVIA | independente do gateway; restringir a mocks/offline até certificação |
| P77B reports/P77B_DEMO_ORDER_CHECK_FILLING_MODE_FIX/p77b_filling_check.py | initialize, symbol_select, order_check em loop de filling modes | ORDER_PRECHECK; NÃO ENVIA | não foi observado gate DEMO antes do order_check; FAIL-CLOSED requerido |
| P79 reports/P79_DEMO_ORDER_AUDIT_POSITION_MONITOR/p79_monitor.py | initialize, account_info, terminal_info, positions_get | ACCOUNT_POSITION_READ; sem envio | consulta conta real possível sem gate DEMO |
| P78 reports/P78_DEMO_ORDER_SEND_SINGLE_CONTROLLED/p78_demo_order_send.py | sem MetaTrader5, order_send ou conexão | DISABLED | bloqueio já aplicado |

**Achado:** não foi identificado `mt5.order_send` nos caminhos residuais acima. `mt5.order_check` NÃO envia ordem, mas conecta-se ao terminal; não autorizar execução real. A existência de conexões independentes do gateway e a ausência de gate prévio em P77B/P79 são gaps de isolamento comprovados por código, não prova de envio real. Para scripts de coleta, classificar como READ_ONLY_MT5_WITH_UNCONTROLLED_TERMINAL_ACCESS até isolamento.

### Subprocess — classificação de comando, entrada e efeitos
| Componente | Chamada | Origem dos argumentos | Efeitos | Classificação |
|---|---|---|---|---|
| app/p1516_multi_family_combo_backtest_executor/engine.py | subprocess.run(string,shell=True) via cmd | REMOTE_NORM/REPORTS constantes, DATA/out caminhos locais; TEMP ambiente | rclone copy Drive→local e local→Drive; retorno ignorado | SHELL_TRUE / REMOTE_WRITE / FAIL_OPEN_ON_COPY_FAILURE |
| app/p1525b_cloud_dataset_reconstruction_fix/engine.py | subprocess.run(string,shell=True) via cmd | REMOTE_NORM/REPORTS constantes, DATA/out locais; TEMP ambiente | Drive→local e local→Drive; retorno ignorado | SHELL_TRUE / REMOTE_WRITE / FAIL_OPEN_ON_COPY_FAILURE |
| app/p153_p155_profit_market_data_pipeline/engine.py | subprocess.run(string,shell=True) via run_cmd | REMOTE_RAW/NORM/REPORTS constantes, RAW/NORM/report_dir locais; TEMP ambiente | Drive→local, local→Drive normalized e reports; retorno ignorado | SHELL_TRUE / REMOTE_WRITE / FAIL_OPEN_ON_COPY_FAILURE |
| app/p156_p1510_real_edge_research_runtime/engine.py | subprocess.run(string,shell=True) via cmd | REMOTE_NORM/REPORTS constantes, DATA/out locais; TEMP ambiente | Drive→local e local→Drive; retorno ignorado | SHELL_TRUE / REMOTE_WRITE / FAIL_OPEN_ON_COPY_FAILURE |
| app/p1621d_real_transcript_fetcher_dataset_matcher/engine.py | import subprocess; nenhuma chamada no arquivo inspecionado | n/a | sem execução subprocess neste arquivo | IMPORT_ONLY |
| app/audits/institutional_healthcheck.py | subprocess.run(cmd,capture_output=True,text=True) | lista de argumentos de pytest | testes locais; sem shell=True observado | TEST_RUNNER_NO_SHELL |

**Achados comprovados:** 4 motores usam shell=True para rclone; todos ignoram returncode, portanto podem publicar relatórios de sucesso após falha de cópia. P15.3–P15.5, P15.16, P15.25B e P15.6–P15.10 escrevem em Drive histórico, contrariando política de fonte imutável se executados. Como os caminhos remotos são constantes, NÃO foi demonstrada injeção por dados de dataset; TEMP é variável de ambiente que influencia caminho e string shell. Não executar os motores sem correção e teste offline. `shutil.rmtree(TMP)` também exige guard de caminho antes de qualquer execução.

### Decisão de certificação
- CLASSIFICATION_GATE=PASS_WITH_LIMITED_SCOPE: classificados os 12 caminhos MT5 e 6 subprocess relacionados; sem rescan global.
- PATCH_GATE=OPEN: aplicar correção mínima para fail-closed em cópias, remover shell=True e impedir escrita no Drive histórico, com mocks e testes específicos. Separar controles para rotas MT5 de leitura/precheck.
- TEST_GATE=NOT_EXECUTED: nenhum teste novo executado nesta atualização; 99/99 históricos não repetidos.
- DRIVE_LEDGER_UPDATE=NOT_EXECUTED; CLOUD_PERSISTENCE_GATE=NOT_EXECUTED.
- PHASE_B=OPEN; REAL_ORDERS=FORBIDDEN; FTMO_REAL=FORBIDDEN.


## ET665.CM.2 — Controles mínimos publicados (2026-11-07)

- P15.16, P15.25B, P15.3–P15.5 e P15.6–P15.10: rclone sem shell=True (argv com shlex), check=True, falhas propagadas; cópia de local para Drive histórico bloqueada por PermissionError; limpeza temporária com verificação do caminho esperado.
- P77B e P79: entrypoints bloqueados em fail-closed antes de qualquer chamada MT5; não equivale a certificação DEMO. P77 e demais rotas MT5 seguem pendentes de isolamento institucional.
- Regressão nova publicada: mind_trader/tests/test_et665_cm2_residual_guards.py (10 casos parametrizados: 4 transferência, 4 cleanup e 2 MT5). **Execução ainda NÃO confirmada**; não declarar PASS. Suíte histórica 99/99 não repetida.
- Os bloqueios de escrita interrompem deliberadamente o fluxo antigo de exportação remota. Manifests/export_ready e promoção de estratégias não devem ser certificados pelo fluxo antigo. Requer destino de artefatos governado distinto do Drive histórico.
- GitHub audit branch somente; sem merge em main. DRIVE_LEDGER_UPDATE=NOT_EXECUTED; CLOUD_PERSISTENCE_GATE=NOT_EXECUTED.

PATCH_GATE=IMPLEMENTED_UNTESTED; TEST_GATE=NOT_EXECUTED; PHASE_B=OPEN; REAL_ORDERS=FORBIDDEN; FTMO_REAL=FORBIDDEN.
