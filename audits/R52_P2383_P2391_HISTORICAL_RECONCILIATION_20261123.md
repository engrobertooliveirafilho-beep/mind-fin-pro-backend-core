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

## Reconciliação P2378/P2379 — fontes primárias do Drive (2026-11-23)
Pastas originais P2378 19r4NeE1RkHSDY1yQAmblv67o46Eqwal7 e P2379 1iROEuK5G5AXWhGU9ZIFFGrS3rEa1LjL8; CSV P2378 promovidos 1zX62swvdS9Vdxl6pNb_taGGMXDo_Dy3G; CSV P2379 PAPER ready 1ct36EPVTVIVkiOjAPJ92a9bXtUlFiQ8D.
Verificação de inventário diretamente sobre os CSVs originais: 699 playbooks promovidos P2378, 164 chaves de contexto distintas (timeframe,regime,session,footprint,lifecycle); 175 linhas com PF proxy=999 e zero perdas. P2379 PAPER ready: 505 sinais distintos por signal_id, porém 96 chaves contextuais distintas; 110 com PF proxy=999. Todas as 505 linhas declaram real_orders=FORBIDDEN e ftmo_real=FORBIDDEN.
Interpretação restrita: signal_id e família não provam edges independentes; PF proxy=999 em ausência de perdas não equivale a PF finito validado fora da amostra. O histórico P2383D posterior confirma 3980 linhas para apenas 796 resultados de mercado distintos e limitações de entrada exata. Não promover ou autorizar execução com base em P2378/P2379 sem recuperação de regra de entrada por preço e proveniência temporal; não alterar arquivos originais do Drive.

## Divergência funcional P2379 — barramento PAPER truncado (2026-11-23)
Fontes originais Drive: ready CSV 1ct36EPVTVIVkiOjAPJ92a9bXtUlFiQ8D (505 linhas); paper_signal_bus CSV 1w2YuvJOaZNixJsTlYNNfzrhiTXCRUqM2 (500 linhas); pasta P2379 1iROEuK5G5AXWhGU9ZIFFGrS3rEa1LjL8. Comparação executada por signal_id: 500/505 ready presentes no bus, 0 entradas extras, 5 ausentes: P2379_CONTEXT_000157 (M30), P2379_CONTEXT_000158 (M1), P2379_CONTEXT_000161 (M30), P2379_CONTEXT_000163 (M15), P2379_CONTEXT_000164 (M1). Todos os cinco são CONTEXT, STANDARD_PAPER, PAPER_ONLY, real_orders=FORBIDDEN. O summary histórico declara explicitamente paper_signal_bus_rows=500 e ready=505; não confundir a declaração CERTIFIED de emissão com prova de entrega integral no barramento.
Pendência: recuperar a implementação original do writer P2379, determinar se houve limite intencional de 500 ou truncamento e aplicar correção somente se a especificação exigir os 505. Não inventar sinal, não alterar CSV histórico, não promover execução real. Testes do writer e E2E ainda não executados nesta missão.

## Confirmação de impacto downstream P2380 (2026-11-23)
Fonte Drive P2380 pasta 1rVmxHZJwh47fvIW03t_efE6BIana50ot; run_p2380.log 1ep7b9s-bZmtpPWzc3cK0nsPoJh6QgcLJ; de40_forward_paper_feedback_all.csv 1djqqQ7NrpM-uQRYrPU0uB9BHpdOhUZbQ. O P2380 consumiu explicitamente o barramento P2379 de 500 linhas, avaliou 500 sinais (não os 505 ready), registrou 243 vitórias, 254 derrotas, WR=0.486, expectancy=-0.083805R, PF=0.832504, maxDD=61.28919R, promoted_after_feedback=0, observed=1, demoted=49. Cinco sinais ready P2379 ausentes do bus também ficaram fora do feedback P2380. Não extrapolar o resultado dos 500 para os 505, nem certificar os cinco ausentes.
A pesquisa do writer original P2379 pelo nome exato no Drive retornou somente pastas de testes e artefatos, não o fonte do escritor; por isso não atribuir causa definitiva ao limite de 500. A especificação histórica registra bus_rows=500, mas não comprova intenção de limitar nem autorização de descartar cinco ready. Próxima ação funcional: recuperar o writer canônico e sua política de cardinalidade; implementar verificação de cobertura por signal_id e testes novos apenas se o contrato exigir 505/505. Manter PAPER_ONLY e nenhuma promoção.
