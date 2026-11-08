# ET665.R67 — Auditoria de rotas residuais e divergência de HEAD (2026-11-08)

## Escopo autenticado
Continuação de R66, commit ancestral `f787a4073fed1695d77f6033b948a05e6703eac3`. Branch nova isolada `audit/et665-r67-residual-routes-20261108`; nenhuma alteração na main, nenhuma ordem, nenhuma conexão MT5, nenhum acesso Drive.

## Achados reproduzíveis por arquivo
- P77, P77B e P79: bloqueios existentes conforme R66; nenhuma certificação de rotas alternativas.
- `mind_trader/reports/P1505_DATA_INGESTION_ENGINE/p1505b_mt5_harvester.py`: `run()` levanta `PermissionError("ET665_MT5_UNCERTIFIED_ENTRYPOINT_BLOCKED")`; o nome do arquivo, isoladamente, não significa conexão ativa.
- `mind_trader/app/p86_execution_intelligence_domain/engine.py`: `mt5_snapshot()` levanta `RuntimeError("ET665_BJ_MT5_CONNECTIVITY_DISABLED_PENDING_SECURITY_REVIEW")`.
- `mind_trader/app/p1621e_real_video_fetch_loop/engine.py`: `fetch_metadata()` e `run()` bloqueiam execução externa com `ET665_BR_EXTERNAL_EXECUTION_DISABLED_PENDING_SECURITY_REVIEW`.
- `mind_trader/app/p1622_autonomous_daily_research_cron/engine.py`: `run_module()` e `run()` possuem o mesmo bloqueio; declaração de `PIPELINE` não é prova de execução.
- `mind_trader/app/p16_autonomous_research_runtime/engine.py` não importa MT5/subprocess; análise local do arquivo não cobre dependências nem outros P16.
- `mind_trader/reports/P1505_DATA_INGESTION_ENGINE/p1505j_merge_diversified_mt5.py`: a observação inicial de indentação inesperada não foi reproduzida na releitura do arquivo atual (blob `0d29e5d4ed9cb555eb5cbf81bb438aed0a3ed4e3`); `for_src = []` está em nível superior e a compilação sintática isolada passou. Nenhuma alteração de código foi necessária.

## Divergência de integração
No momento da consulta, PR #3 permanecia `draft`, head `55ea36b6af6baea69f1ea1283eecf7fa1524155d` e base `main` `1b5916fbdc8c90173061315400abb92f3bbbb13a`. R66 `f787a407` não é esse HEAD. **Não confundir teste ou relatório em R66/R67 com teste do HEAD do PR #3**.

## Testes novos
`mind_trader/tests/security_review/test_et665_r67_residual_route_guards.py` — regressões AST-only para as sete rotas selecionadas e dois cenários estruturais adicionais. Publicados, não executados neste passo; não representam varredura global, importação de módulos, teste de rede nem isolamento de runtime.

## Contexto de riscos mantidos
R24 historicamente reporta 37.784 arquivos Python enumerados, 6.900 sinalizados e 39 falhas AST. Essas contagens pertencem ao commit R23/R24, **não** a este HEAD. A resposta recursiva GitHub atual informa `truncated=true`; não é inventário completo. R29 havia publicado proteções em 18 espelhos, sem prova global de alcançabilidade.

## Gates B01–B12
B01/B02: bloqueio estático confirmado por inspeção anterior, isolamento institucional ABERTO. B03/B04: revisão focal ampliada, ABERTO. B05: parcial. B06/B07: autoridade do manifesto e reconciliação REAL ABERTAS. B08: parcial. B09: testes R67 preparados, regressão consolidada ABERTA. B10: integração PAPER ABERTA. B11/B12: parecer e fechamento ABERTOS.

Próxima etapa: executar testes offline sem MT5/rede, coletar JUnit + SHA-256 em um único SHA, reconciliar históricos e inspecionar chamadas dinâmicas/espelhos e subprocessos remanescentes antes de qualquer certificação.

`CUSTO_ALVO=R$0,00 | FASE_B=ABERTA | ORDENS_REAIS=PROIBIDAS | MAIN=INTACTA | R67_TESTS=NOT_EXECUTED`


## Follow-up estático R67 — 2026-11-08
- P77, P77B, P79 e P1505B: os quatro entrypoints inspecionados começam com bloqueio explícito antes de qualquer acesso MT5.
- P86: mt5_snapshot() inicia com bloqueio após docstring; a suíte AST foi ajustada para ignorar docstring ao verificar a primeira instrução executável.
- P1621E e P1622: entrypoints externos e run() bloqueados antes de subprocesso/rede.
- O ajuste da suíte foi publicado no commit 20bf226ba818aff8cceae798b044a7feba347ec5; ainda NÃO executado no Docker offline.
