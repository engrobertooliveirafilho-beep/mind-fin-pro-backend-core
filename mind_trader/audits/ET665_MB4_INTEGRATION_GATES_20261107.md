# ET665.MB.4 — Gates independentes da macroetapa

Data: 2026-11-07

## Inspeção
- P15.16: relatório local e staging p1516; Drive somente como origem de leitura.
- P15.25B: relatório local e staging p1525b; Drive somente como origem de leitura.
- P15.3–P15.5: CSV bruto de leitura, normalização local e staging p153_p155; sem upload normalizado.
- P15.6–P15.10: pesquisa sobre CSV normalizado e staging p156_p1510; sem upload.

## Mudança
- Executor exige 50 testes sem falhas/erros/skips **e** presença no JUnit de 8 casos nomeados: execução integrada e rejeição de escrita para cada um dos 4 motores.
- `p15_synthetic_end_to_end` só recebe `PASS_SYNTHETIC` quando esses oito casos estão presentes e a suíte completa aprova.
- Suíte aprovada sem casos nomeados continua BLOCKED.

## Pendente
- Testes novos e macro runner não executados neste ambiente; não afirmar PASS.
- Revisão independente de segurança, inventário residual completo e publicação governada ainda sem certificação.
- Fase B bloqueada. Ordens reais proibidas.

ET665_MB4_CODE=PUBLISHED
ET665_MB4_TESTS=PENDING
PHASE_B=BLOCKED
REAL_ORDERS=FORBIDDEN
FTMO_REAL=FORBIDDEN
