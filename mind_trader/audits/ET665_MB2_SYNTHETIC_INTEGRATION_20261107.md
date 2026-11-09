# ET665.MB.2 — Integração sintética P15

Data: 2026-11-07. Branch isolada.

## Implementação
- Quatro testes de execução `run()` dos motores P15.16, P15.25B, P15.3–P15.5 e P15.6–P15.10.
- Datasets sintéticos locais de 180 barras, fila e edges sintéticos. Chamadas de leitura `rclone copy` substituídas por função offline que exige origem `gdrive:` e gera dados locais. Sem acesso à rede, corretora, MT5 ou Drive.
- Valida produção de relatórios, pacote de evidências offline, manifestos de segurança e limpeza de scratch.
- Executor macro agora coleta 46 testes: 42 regressões + 4 integrações sintéticas.

## Limitações
- Código e testes publicados, **ainda não executados**. Integração sintética não prova funcionamento com Drive real nem valida estratégia/FTMO.
- `PHASE_B` permanece BLOCKED por inventário residual, revisão independente de segurança e publicação governada não certificadas.
- Nenhum GitHub Actions acionado, nenhum custo autorizado.

ET665_MB2_CODE=PUBLISHED
ET665_MB2_TESTS=PENDING
PHASE_B=BLOCKED
REAL_ORDERS=FORBIDDEN
FTMO_REAL=FORBIDDEN
