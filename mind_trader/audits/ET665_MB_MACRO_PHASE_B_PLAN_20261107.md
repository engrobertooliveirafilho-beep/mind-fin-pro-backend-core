# ET665.MB — Macroetapa única de consolidação da Fase B

Data: 2026-11-07. Branch isolada, sem merge na main.

## Entregue
- Executor offline `mind_trader/security/et665_mb_phase_b_runner.py`.
- Uma invocação executa 42 regressões focadas (CM4/CM5/CM6/CM7), captura JUnit e log, calcula SHA-256, produz `decision.json` e ZIP.
- Não aciona rclone, MT5, corretora, GitHub Actions, Drive ou APIs pagas. Sem credenciais.
- Falha fechada: aprovação das 42 regressões **não** implica `PHASE_B_PASS`.

## Bloqueios explícitos
- Execução integrada sintética P15: não certificada.
- Inventário residual completo: não certificado.
- Revisão independente de segurança: não certificada.
- Publicação governada GitHub: não certificada.

## Limitações
- Este é o **primeiro componente** da macroetapa, não o fechamento integral.
- Executor ainda não foi executado neste ambiente; requer teste local isolado e inspeção do ZIP.
- `PHASE_B=BLOCKED` por design até os gates restantes serem implementados, testados e aprovados.
- R$0 de serviços pagos, `REAL_ORDERS=FORBIDDEN`, `FTMO_REAL=FORBIDDEN`.
