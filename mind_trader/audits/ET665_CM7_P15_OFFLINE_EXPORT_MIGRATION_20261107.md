# ET665.CM.7 — Integração P15 com preparação offline
Data: 2026-11-07

## Código alterado
- P15.16, P15.25B, P15.3–P15.5 e P15.6–P15.10: comandos de upload de relatórios para Drive histórico substituídos por `stage_engine_report`, que gera pacote local com manifesto SHA-256 sob TEMP.
- P15.3–P15.5: upload de dados normalizados ao Drive histórico removido. Dados permanecem na área de trabalho temporária até limpeza segura.
- Funções `cmd/run_cmd` continuam permitindo somente cópias de leitura `gdrive:` -> local, com `shell=False` e `check=True`.
- O stager não acessa GitHub, rede ou Drive e não concede autorização de publicação. A inspeção de segredos é heurística; revisão antes de publicar é obrigatória.
- 8 regressões estruturais adicionadas em `mind_trader/tests/test_et665_cm7_p15_offline_exports.py`.

## Pendências e riscos
- Testes CM7 não executados: **não declarar PASS**.
- Não houve execução ponta a ponta dos quatro motores com datasets reais.
- A importação de `mind_trader.security` pressupõe raiz do repositório no PYTHONPATH; validar forma de invocação original.
- Limites do stager (100 arquivos, 8 MiB cada) podem bloquear relatórios maiores; fail-closed é intencional.
- Revisão formal de segurança, inventário residual e autorização para Fase C pendentes.

CM7_CODE=PUBLISHED
CM7_TESTS=PENDING
PHASE_B=OPEN
REAL_ORDERS=FORBIDDEN
FTMO_REAL=FORBIDDEN
