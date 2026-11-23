# P2376–P2382 — Auditoria de causalidade e integridade
Data: 2026-11-23
Repositório: engrobertooliveirafilho-beep/mind-fin-pro-backend-core
Base inspecionada: main @ 1b5916fbdc8c90173061315400abb92f3bbbb13a
Branch isolada: audit/p2376-p2382-causal-integrity-20261123

## Decisão executiva
P2376 é recuperável como detector retrospectivo de eventos e gerador de rótulos pós-evento; seus campos post-MFE/MAE não podem ser usados como features de decisão no instante do sinal.
P2377–P2382 NÃO estão certificados para evidência causal, seleção de estratégia, replay ou edge. Os artefatos históricos permanecem preservados, mas devem ser marcados como INVALID_FOR_CAUSAL_PERFORMANCE.
Nenhuma alteração em main, runtime de produção ou fontes originais foi feita. REAL_ORDERS=FORBIDDEN; FTMO_REAL=FORBIDDEN; PAPER_ONLY.

## Reconciliação histórica do Drive
- P2376: 46.131 eventos e contextos; footprints rotulados INFERRED_NOT_CONFIRMED. O módulo calcula janelas futuras de 20 candles para post_mfe_atr, post_mae_atr, post_followthrough e post_efficiency.
- P2377: 46.131 eventos roteados; 22.641 candidatos PAPER e 23.490 bloqueados. O log histórico declara CERTIFIED, mas a implementação consumia variáveis pós-evento.
- P2378: 22.641 candidatos; 4.266 playbooks e 699 promovidos. O log declara CERTIFIED, mas o score/outcome usa MFE/MAE/efficiency posteriores.
- P2379: 916 sinais, 505 prontos, 411 observe-only. São sinais de arquivo/template, não ordens reais nem execução forward temporal comprovada.
- P2380: 500 sinais avaliados; 243 wins, 254 losses; expectancy -0.083805R; PF 0.832504; DD 61.28919R. A simulação usa índice derivado de hash(signal_id), não timestamp do sinal; o hash do Python é randomizado por processo, logo o ponto de entrada não é reprodutível entre execuções.
- P2381: 254 nós de perda, 5 clusters, 227 candidatos. A função apply_patch remove explicitamente toda linha com realized_r < 0, além de regras BLOCK. Isso seleciona apenas não-perdas para o replay.
- P2382: 227 candidatos resultam em 224 wins e 0 losses, PF 999 e DD 0. A ausência de perdas é explicada pelo filtro de P2381, não prova melhora de edge. O próprio resumo informa 0 grupos promovidos e 8 observados.

## Defeitos reproduzidos por inspeção estática do código publicado em main
1. P2376 `context_window()` calcula MFE/MAE/follow-through com candles futuros. Isoladamente, isso pode servir para rótulo retrospectivo; não pode ser feature disponível no candle de decisão.
2. P2377 `classify_lifecycle()` usa post_mfe_atr, post_mae_atr e post_followthrough para classificar lifecycle; `context_score()` usa post_efficiency. O roteador, portanto, usa informação futura.
3. P2378 `infer_context_result()` transforma post_mfe_atr/post_mae_atr/post_efficiency em resultado e expectancy proxy, e promove playbooks com esses resultados. A promoção é contaminada por look-ahead.
4. P2379 emite sinais derivados dos playbooks/contextos promovidos por P2378. Consequentemente, seus 505 sinais prontos herdam a contaminação.
5. P2380 `index_for_signal()` usa `abs(hash(signal_id))` para escolher o candle de entrada; isso não representa emissão temporal real e não é determinístico entre processos Python.
6. P2381 `apply_patch()` descarta toda observação com `realized_r < 0`; o conjunto de replay é condicionado ao resultado. Isso invalida qualquer comparação posterior.
7. P2382 calcula estatísticas sobre a amostra já filtrada por P2381; a taxa de perdas zero é consequência do viés de seleção.

## Correção exigida — ordem de trabalho
G1 — Separar feature temporal e rótulo retrospectivo: manter post-MFE/MAE apenas em labels/outcomes, nunca em router, score, lifecycle ou promoção no timestamp do evento.
G2 — Reconstruir P2377 com features disponíveis até o fechamento do candle de sinal; entrada somente no próximo preço executável/candle, com timestamps UTC e symbol explícito.
G3 — Recalcular P2378 usando outcomes de trade obtidos por simulação causal independente, não MFE/MAE futuro como proxy de resultado.
G4 — P2379 deve emitir eventos timestamp-bound, com signal_id estável, symbol, event_time, source_row_hash e lineage do playbook; remover sinais-template sem timestamp.
G5 — P2380 deve consumir esses eventos em ordem temporal e usar índice obtido por timestamp/índice de origem, nunca hash() para escolher entradas. Modelar spread, slippage, comissão, gaps e prioridade intrabar stop/target.
G6 — P2381 deve aplicar bloqueios/quarentena apenas a partir de amostra de treino; nunca remover perdas do conjunto de avaliação. Separar treino, validação e teste cronologicamente.
G7 — P2382 deve reexecutar todos os candidatos elegíveis, incluindo perdas e rejeitados; comparar baseline e patch no mesmo conjunto OOS, com hashes e ledger por trade.
G8 — Walk-forward purgado/embargado, custos e múltiplos períodos; promoção somente após critérios pré-registrados e evidência independente.

## Gates e status
- SOURCE_RECOVERY: PASS (fontes P2376–P2382 encontradas em main).
- STATIC_CAUSAL_AUDIT: FAIL (look-ahead e seleção por resultado identificados).
- HISTORICAL_LOG_RECONCILIATION: PASS (logs P2377–P2382 encontrados no Drive).
- REPLAY_REPRODUCIBILITY: FAIL (P2380 hash anchor; P2381 loss filtering).
- OOS_EDGE_CERTIFICATION: NOT_CERTIFIED.
- CODE_PATCH: NOT_APPLIED.
- TEST_EXECUTION: NOT_RUN nesta auditoria.
- MAIN_INTACT: TRUE.
- REAL_ORDERS / FTMO_REAL: FORBIDDEN.

## Fontes de evidência
Drive:
- P2377 log: https://drive.google.com/file/d/12Fy3qj0PWm1S6sPdOAsIYqxJHUFR4Gq8/view
- P2378 log: https://drive.google.com/file/d/1hwdmdMEIHAcORxKk_wa2L06blFMp2BlR/view
- P2379 log: https://drive.google.com/file/d/1WPdM8DeU-n_Vi3sN-oA1G2KrwjdKYF1P/view
- P2380 log: https://drive.google.com/file/d/1ep7b9s-bZmtpPWzc3cK0nsPoJh6QgcLJ/view
- P2381 log: https://drive.google.com/file/d/1z12joSqGu9qmPMYr-oN_7xylvS4zOLNv/view
- P2382 log: https://drive.google.com/file/d/1KaKAHMorTB7DV3VQoIFb6B01VSdOooTd/view
- Dossiê P2368–P2382: https://drive.google.com/file/d/16x5f7suH3oUcdfL4TShGzu3Obpom93C5/view

GitHub source blob SHAs:
- P2376: de50c447cd77df673a9fe42bde5cae0a69abc573
- P2377: fdc826403a84f76d07b894b634ed3641f4942896
- P2378: ebc491833cfe29d18666710cbb757b96c9895253
- P2379: 23cfcb188d684350112acdc733e2d761e0e9e444
- P2380: c8971714e0543e74c66424f8879960d8dea98dc8
- P2381: 94792b12a2baad20742ef39111ca5228738861e4
- P2382: 669df7d3dd9905ea542295aa6c7b08c7cf030d45

Observação: os logs históricos registram certificações operacionais, mas não substituem a validação causal do código-fonte. A branch causal informada anteriormente (5870b173) não foi localizada/read-back confirmada neste repositório durante esta auditoria; o arquivo P2377 em main continua contendo os campos pós-evento.
