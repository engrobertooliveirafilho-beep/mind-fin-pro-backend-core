# ET665.R76 — Evidência CI do teste estrutural (2026-11-08)

- SHA testado: `4a07ac4c732638405ad16297a86b33a142a3f1c0`.
- GitHub Actions run: `42478226598`; job `128724245114`, conclusão `success`.
- Etapas confirmadas: checkout `success`, execução de regressão offline `success`, upload `success`.
- Artefato: `et665-r73-offline-evidence`, ID `13616731082`, tamanho 1393 bytes, digest ZIP `sha256:a75c51450dd050ff3589c6d19359c54e8dda7f31321a72f33d00de31608418d3`.
- URL: https://github.com/engrobertooliveirafilho-beep/mind-fin-pro-backend-core/actions/runs/42478226598
- Escopo: quatro métodos de unittest, incluindo nove subtestes de guardas MT5/subprocessos, gateway PAPER source-only, parse P1505J e imports do teste. Não é teste E2E nem comprova isolamento de rede/terminal.
- Workflow R338 legado ainda falha separadamente por configuração/credenciais; **não confundir com o CI R73 PASS**.
- A revisão não inspecionou individualmente o conteúdo do ZIP, embora o upload e digest sejam confirmados pela API.
- B09: regressão estática executada PASS, suíte histórica completa ainda pendente. B01–B08 e B10–B12 continuam abertos.

`PHASE_B=OPEN | STATIC_CI=PASS | PAPER_E2E=NOT_CERTIFIED | REAL_ORDERS=FORBIDDEN | MAIN=UNTOUCHED`
