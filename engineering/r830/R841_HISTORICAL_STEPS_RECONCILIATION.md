# R841 — Reconciliação de inventários históricos de STEPs
Data da reconciliação: 2026-11-22. Fontes originais recuperadas e analisadas no Google Drive.

| Fonte | Drive file ID | Itens | Estado |
|---|---|---:|---|
| MIND_STEPS.json.txt | `13XKa0uDyLBWJpg-CTRPnYBZUcllS7b4t` | 300 | 17 `done`; 283 `unknown` |
| MIND_STEPS_PHASE1_STATUS_PLAN.json.txt | `1Ua88QWKIna9GyZScenCTceioCrbTPt02` | 25 | 25 `nao_validado`; `status_dev` e `status_prod` desconhecidos |
| MIND_STEPS_WAVE1_EXEC.json.txt | `1-MOEDRZxfANWiUU-o14V0VcMTO0kW47a` | 40 | planejamento com títulos; sem campo de certificação por STEP |

Todos os três JSONs foram parseados; contagens e unicidade dos identificadores verificadas; o plano Wave1 declara `total_steps=40` e contém 40 itens. Último número do plano é 90, portanto seus 40 itens **não** são sequência contínua 1–40.

**Não reconciliar os estados por igualdade numérica de STEP sem confrontar semântica, revisão e evidência.** Os 17 `done` do inventário 1–300 têm como `notes` detecção em `conversations.json`; isso não prova código, testes ou execução. Os 25 `nao_validado` do plano Fase1 não devem ser substituídos por `done` sem prova adicional.

Outros achados preservados: R840 recuperou `dev.step_planner_agent` como `not_implemented`/`stub`; R836 localizou 58/58 módulos do manifesto histórico; nenhum foi promovido.

Próximo gate: ligar cada STEP a `path_canonical`, SHA-256 calculado de bytes, teste offline e consumidor real; só então avaliar promoção. Não executar nem alterar runtime histórico, main ou produção.
