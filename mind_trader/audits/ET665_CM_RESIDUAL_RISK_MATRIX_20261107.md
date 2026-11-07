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
