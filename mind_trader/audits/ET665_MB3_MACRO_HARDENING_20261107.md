# ET665.MB.3 — Hardening da macroetapa

Data: 2026-11-07. Branch isolada.

## Alterações
- 4 testes negativos novos: cada guard P15 deve rejeitar `rclone copy local -> gdrive:` com `PermissionError` antes de qualquer subprocesso.
- Nos 4 testes sintéticos, subprocessos reais e conexões socket são proibidos por monkeypatch. `rclone` de leitura é simulado somente em memória/local.
- Macro runner agora exige saída dentro de TEMP, rejeita overwrite do ZIP, captura timeout em 180s, trata JUnit inválido e exige exatamente 50 testes sem falhas/erros/skips.
- JUnit, log, decisão e ZIP produzidos em uma invocação. Nenhum deploy, merge, publicação automática ou autorização de ordens.

## Certificação
- **50 testes preparados, não executados nesta revisão**. Nenhuma alegação de PASS.
- `phase_b=BLOCKED` permanece obrigatório, mesmo com 50/50, pois inventário residual, revisão independente e publicação governada continuam não certificados.
- O executor não implementa auditoria completa nem aprovação formal de segurança.

CM8_CODE=PUBLISHED
CM8_TESTS=PENDING
PHASE_B=BLOCKED
REAL_ORDERS=FORBIDDEN
FTMO_REAL=FORBIDDEN
