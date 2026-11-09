# ET665.R318 — Preservação de referência R315 e triagem comportamental

Data de registro: 2026-11-09. Escopo: somente PAPER/DEMO, sem produção, sem merge.

## Evidência R315 — transcrição fornecida pelo operador

- Branch: `audit/et665-r308-paper-session-guard-20261109`
- Commit testado: `cb368cecd3d1d576f31fde0e840543de6b36b11e`
- Comando relatado: Docker offline, `--network=none --read-only --cap-drop=ALL --security-opt=no-new-privileges --user=65534:65534`, pytest nos dez arquivos de teste R315.
- Saída fornecida: `30 passed in 1.62s`; `EXIT_CODE=0`; `GIT_STATUS=CLEAN`.
- Caminho **na máquina do operador**, não acessível ao GitHub: `D:\MIND_T~1\SYSTEM~1\ET665_R315_RETEST_20261109_154141`.
- **Proveniência:** resultado preservado aqui como transcrição do operador. NÃO é cópia do log bruto; hashes SHA256 do log e runner ainda não verificados. Nenhum workflow CI foi localizado para esse commit na consulta anterior.

## Testes comportamentais já existentes no mesmo commit — NÃO REIMPLEMENTAR

1. `mind_trader/tests/test_p849_gateway_paper_session_integration.py`: cinco cenários (sem sessão, sessão aberta, sessão encerrada, replay sem sessão, limite diário). Testes inspecionados; **execução atual ainda não comprovada**.
2. `mind_trader/tests/test_p896_gateway_paper_broker_integration.py`: três cenários (aceitação simulada, rejeição antes do broker, bloqueio LIVE). Testes inspecionados; **execução atual ainda não comprovada**.
3. `mind_trader/tests/test_p16_autonomous_research_runtime.py`: quatro cenários (walk-forward, Monte Carlo, decay, manifest PAPER). São verificações funcionais parciais; não comprovam isolamento de subprocesso/rede.

**Primeira bateria incremental:** executar apenas esses três arquivos em Docker offline isolado, com cópia do source para tmpfs, logs + exit code + SHA256; não repetir a bateria R315 de 30 testes.

## Gaps após a bateria incremental

- MT5 P77/P79: testar bloqueio de terminal/conta não autorizados sem credenciais reais.
- P15/P16: isolamento efetivo de subprocesso, rede, arquivos e credenciais.
- Gateway PAPER: falhas adversariais, fill ausente, reserva de capacidade e concorrência.
- HP19: 19 contratos funcionais positivos/negativos com evidência individual; 11 negativos históricos não bastam.
- Datasets: reconciliar manifests originais antes de remover fail-closed P15.15.
- Drive/Git R60: preservar logs e hashes com vínculo ao commit, sem varredura global.

## Regras de certificação

`FASE_B=0/16`; `HP19=0/19` até evidência individual auditável. `REAL_ORDERS=FORBIDDEN`; `FTMO_REAL=FORBIDDEN`; `COST=R$0`. PR em Draft, main intacta, sem merge.
