# R52 — Reconciliação P2383–P2391 (2026-11-23)

Fonte histórica: Drive, DOSSIE_AUDITORIA_PROFUNDA_P2383_P2391.pdf (ID 1-qBzDz-p6ct7u0Un37FFrlDvOhcev_1O). O dossiê declara expressamente que resume o informado/validado na conversa histórica; NÃO constitui prova de execução atual ou certificação independente.

## Não refazer
P2383 falha de granularidade; P2383B agregações; P2383C parser MetaTrader; P2383C2 normalização ATR; P2383D reconstrução contextual; P2384/P2384A transições; P2385 filtro PAPER; P2386B schema entry_time→time; P2387 ponte MT5 PAPER; P2388 monitor; P2388A/B/C grafo; P2389 Governance Lock; P2390 testes; P2391 pesquisa de edge.

## Métricas declaradas no dossiê
P2385: 920 candidatos, 230 PAPER, 690 bloqueados, PF=1.543464, WR=56.521739%, expectancy=0.104782R.
P2388: 230 learning events, NetR=24.099759.
P2391: 99.998 eventos, 4.288 candidatos, 40 promovidos, 352 observados, 3.896 rejeitados. Melhor candidato PF=4.161794, WR=63.33%, expectancy=0.279106R.

## Interlock de evidência
O arquivo descreve artefatos originais em C:\Users\MindFin\Desktop\mind-fin-pro-backend-core_evidence\P2383...P2391; tais artefatos não foram verificados nesta missão. Não confundir certificação histórica declarada com E2E atual.
Código R51: commit bb23ac6b8d89ce1629b78b2b72eaede0e0ba3ba6, leitura GitHub verificada; pytest ainda não executado. Tentativa de recuperar raw.githubusercontent.com no container falhou por DNS (curl:6); não declarar regressão PASS.
Próxima ação: recuperar fontes e evidências originais P2392, conectar o gate ao executor legado, executar pytest do commit exato e auditar walk-forward/temporal leakage.
PAPER_ONLY=TRUE | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN | MAIN=INTACTA | E2E_CERTIFIED=FALSE | COST=R$0

## Reconciliação posterior com CSVs P2383D originais (2026-11-23)
Fonte Drive: pasta P2383D_EXACT_PLAYBOOK_TO_RAW_CANDLE_VALIDATOR_20260624_141656 (1ZuNFZoqaLm9G9_de4E0GEWwruLyTPa7M); matched trades CSV 1FtHS_xASRVJmHbifpwcNBcib6PWuor5a; promoted CSV 1ET0vqkahnlDJ6xZG7imv_19vU9UAWy5b; timeframe audit 1yn2A_w2L2gjBBJfldaolsFwCMsaxTSn4.
Reconciliação executada sobre 3.980 linhas de trades: 796 chaves distintas (entry_time,symbol,timeframe,regime,session,footprint,lifecycle,direction,atr,entry_close,next_close,realized_r); cada chave aparece exatamente 5 vezes, vinculada a playbooks diferentes. Cinco playbooks promovidos compartilham exatamente um contexto e um perfil idêntico de métricas. A contagem de linhas não demonstra 3.980 resultados de mercado independentes; o número de resultados distintos é 796. Não atribuir diversificação ou cinco edges independentes com base nesses dados.
Timeframe audit: M1 PF=0.981497, M5 PF=0.862237, M15 PF=1.226831; M30/H1/H4/D1 sem operações casadas. Todos os timeframes com passed=False; DD global P2383D=111.593895R. O próprio summary P2383D reconhece que a validação é contextual e não reconstrói entradas exatas por preço/tick, apesar de declarar original_p2382_edge_certified=true. Esta declaração não substitui prova independente.
Decisão: não promover P2383D/P2382; preservar as saídas históricas sem modificação; exigir fonte exata da entrada, deduplicação por evento e auditoria OOS independente antes de integrar ao executor. Esta é reconciliação de evidência, não nova execução de backtest ou certificação E2E.
