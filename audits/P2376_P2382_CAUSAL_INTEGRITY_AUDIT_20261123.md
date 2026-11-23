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


## ADENDO DE RECONCILIAÇÃO DRIVE/GITHUB — 2026-11-23

### Correção de escopo e etapas já concluídas
A auditoria inicial desta branch deve ser lida com este adendo. A inspeção do MASTER REMEDIATION LEDGER e dos dossiês posteriores revelou que a cadeia não parou em P2382:
- P2383B/C/C2/D, P2384/A e P2385–P2391 foram executados historicamente; não reiniciar.
- P2385: 920 candidatos, 230 PAPER e 690 bloqueados; PF 1.543464, WR 56.521739%, expectancy 0.104782R (números documentais).
- P2386B reparou schema entry_time→time; P2387 validou a ponte MT5 PAPER; P2388 monitorou 230 eventos forward PAPER com NetR 24.099759; P2389 Governance Lock; P2390 suíte PAPER; P2391 99.998 eventos, 4.288 candidatos, 40 promovidos, 352 observados e 3.896 rejeitados. Esses resultados são históricos e não equivalem a edge OOS independente.
- P2384 teve um corte anterior com 0/3 ciclos promovidos e P2385_ALLOWED=False; a documentação posterior registra P2384/A transições aprovadas e P2385 executado. O estado posterior prevalece no escopo histórico, mas a certificação de rentabilidade continua não demonstrada.
- P2392 foi recuperado e reproduzido em ET-499 (2026-11-03): executor original SHA256 dffc5e1a1f2b8e6e0bfc639fd4c6f3533d77668d20fa67468a4f8edf9fb83037; 40 candidatos, 1 promovido, 1 observado, 38 rejeitados; seis CSVs de saída 6/6 byte-idênticos ao Drive. Melhor edge reportado: 152 eventos, 4/5 janelas, PF 1.715719, WR 59.210526%, DD 4.158651R, expectancy 0.139817R. ET-501 validou o Governance Guard isolado e controles de adulteração.
- Limite de P2392: reprodução histórica determinística comprovada; proveniência independente da série M15/broker, custos, causalidade operacional, integração CI e FTMO não certificados. Não repetir a recuperação/reprodução P2392.
- Dossiês P2405–P2614 registram Edge Pool/Risk/Factory/Walk Forward/Ensemble/Router/Paper, P2409–P2415 Paper Stack, P2500–P2510 5.393 capabilities/switchboard/runtime lock, P2601–P2610 Edge Research Platform, P2611 GER40, P2612 replay USD 100 e P2613 hardening; P2614 define replay modular. São autoridade histórica documental, exigindo reconciliação por código/hash antes de qualquer reutilização.
- O repositório `engrobertooliveirafilho-beep/eldora-trader` identifica-se no README como futuro repositório de código consolidado; lista R27 PAPER OOS com 148 testes em fixtures, mas não declara importação completa do código R1–R27. Branch histórica localizada: `audit/p2405f-causal-walk-forward-gate-20261116`. Não substituir autoridade nem copiar implementação sem recuperar e comparar fontes.

### Reconciliação do P2377 anterior
O histórico de continuidade contém referência a uma correção/gate P2377 anterior (`2939136a`, testes causais 3/3 e gate `5870b173`, 5/5) em branch isolada. A busca desta sessão não conseguiu localizar/read-back esses commits no repositório `mind-fin-pro-backend-core`; isso NÃO prova que nunca existiram ou que estejam ausentes de outro repositório/branch. Portanto:
- Não refazer a correção antes de recuperar o branch/commit original.
- O arquivo P2377 em `main` deste repositório, blob `fdc826403a84f76d07b894b634ed3641f4942896`, continua usando `post_mfe_atr`, `post_mae_atr`, `post_followthrough` em `classify_lifecycle` e `post_efficiency` em `context_score`; a correção histórica ainda não foi demonstrada integrada a esse arquivo.
- P2376 pode continuar calculando métricas futuras para rótulos retrospectivos; o bloqueio é seu consumo como feature de decisão no P2377.

### Gate reutilizável publicado nesta branch
- `app/runtime/p2376_p2382_causal_integrity_gate.py`
- `tests/test_p2376_p2382_causal_integrity_gate.py`
- Testes locais executados: 14/14 PASS; `compileall` PASS.
- Read-back GitHub: blob do módulo `6fbec9cb6bf4248eb4f12ce3a09046aacd3c2b44`; blob dos testes `bfe6644e10596eb2ef9ca87a85a7541ed44fadab`.
- O gate cobre rejeição de features pós-evento, timestamps UTC, primeiro candle estritamente posterior, símbolo consistente, identidade determinística por SHA-256, filtros treinados sem excluir perdas e PF indefinido quando não há perdas.
- LIMITAÇÃO: módulo auxiliar ainda NÃO está conectado a P2377/P2380/P2381/P2382; os 14 testes certificam somente o contrato isolado, não os motores legados nem replay financeiro.

### Próxima sequência correta — sem retrabalho
1. Recuperar e comparar o branch/commit P2377 anterior (`2939136a`/`5870b173`) em todos os repositórios e reconciliar com o blob atual.
2. Se a correção não estiver integrada, aplicar patch mínimo em branch isolada ao P2377 original; separar features contemporâneas de outcomes pós-evento.
3. Integrar os gates do módulo auxiliar somente após testes de contrato e regressão do motor original.
4. Reconciliar P2380/P2381/P2382 com os artefatos ET-499/501 e P2405F/R27; não repetir P2392 nem walk-forward já reproduzido.
5. Só então executar teste causal em dados de mercado cuja proveniência, custos e contrato GER40 estejam autenticados. Nenhuma promoção por resultado histórico.

### Status atualizado
- DRIVE_HISTORY_P2383_P2391: RECUPERADO.
- P2392: REPRODUÇÃO HISTÓRICA 6/6 OUTPUTS IDÊNTICOS; NÃO EDGE CERTIFICATION.
- P2405_P2614: DOCUMENTADOS; AUTORIDADE DE CÓDIGO/HASH A RECONCILIAR.
- CAUSAL_GATE_HELPER: PUBLICADO; 14/14 TESTS LOCAIS PASS; READ-BACK PASS.
- P2377_RUNTIME_INTEGRATION: PENDING.
- P2380_P2382_CAUSAL_REPLAY: PENDING.
- MAIN_INTACT=TRUE; PAPER_ONLY=TRUE; REAL_ORDERS=FORBIDDEN; FTMO_REAL=FORBIDDEN; COST=R$0.


## CORREÇÃO DE RECONCILIAÇÃO — P2377 CAUSAL FIX RECUPERADO (2026-11-23)

A declaração anterior de que o commit P2377 não havia sido localizado fica SUPERADA por recuperação posterior nesta sessão.

- Commit histórico recuperado: `2939136a`.
- Arquivo corrigido: `app/runtime/p2377_de40_regime_first_signal_router_with_xray_lifecycle.py`.
- Blob SHA: `32a359501563caafed8c48790dfebbad45d1d5f5`.
- Branch nova de recuperação: `audit/p2377-causal-recovery-20261123`, criada diretamente a partir do commit `2939136a`.
- Leitura posterior da branch confirmou o mesmo blob SHA.
- O código corrigido faz `classify_lifecycle()` ignorar totalmente o context futuro, retornar lifecycle `*_DETECTED_UNCONFIRMED` com score 0; remove `post_efficiency` do `context_score()`; define `BLOCK_UNCERTIFIED_CAUSAL_LIFECYCLE` para todos os eventos; e não exporta labels pós-evento para router/library.
- A referência histórica `5870b173`, quando resolvida para este caminho de arquivo nesta sessão, retornou o blob antigo `fdc826403a84f76d07b894b634ed3641f4942896`, igual ao arquivo contaminado de `main`; portanto, não deve ser confundida com o patch efetivo. O patch de fonte recuperado é `2939136a`.

### Regressão nova
- Publicado `tests/test_p2377_causal_recovery_20261123.py` na branch de recuperação.
- Commit: `df3a88ad61bc214ffa006aca638cbfc2c104faea`.
- Read-back do teste: blob `e868f89692c24c484e4ce79f54aba70605fbd8f3`.
- 3 testes: lifecycle invariável a contextos futuros; score invariável a post_efficiency; router fail-closed e exportações sem labels futuros.
- Execução local no espelho funcional reconstruído a partir da fonte recuperada: 3/3 PASS. Limite: não foi executado GitHub Actions/CI, e o arquivo local de teste não foi verificado byte-a-byte contra o blob remoto da fonte. Histórico anterior também registra 3/3 PASS e gate 5/5, mas os artefatos de teste históricos não foram localizados neste read-back.

### Estado correto após recuperação
- P2377_CAUSAL_SOURCE_FIX: RECOVERED.
- P2377_CAUSAL_REGRESSION: 3/3 PASS LOCAL MIRROR; CI PENDING.
- P2377_MAIN_INTEGRATION: NOT DONE; main permanece com o blob contaminado `fdc826403a84f76d07b894b634ed3641f4942896`.
- Não reaplicar o patch: reutilizar a branch/commit recuperados e fazer apenas integração controlada após regressão do código exato.
