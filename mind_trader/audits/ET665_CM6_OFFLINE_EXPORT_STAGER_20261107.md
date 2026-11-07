# ET665.CM.6 — Exportação governada: implementação inicial

Implementado um **stager offline** com manifesto SHA-256 em `mind_trader/security/et665_cm6_evidence_stager.py`, e 8 testes focados em `mind_trader/tests/test_et665_cm6_evidence_stager.py`.

Escopo: somente cópia de arquivos permitidos para subdiretório novo de TEMP, sem rede, credenciais, GitHub push ou rclone. Proíbe sobrescrita, links simbólicos, arquivos com nomes sensíveis, marcadores comuns de segredo, caminhos externos ao TEMP, extensões não permitidas, arquivos >8 MiB e lotes >100. Verifica SHA-256 após cópia. Manifesto declara STAGED_FOR_REVIEW_NOT_PUBLISHED.

**Importante:** proteção de segredos é apenas heurística; revisão humana antes da publicação é obrigatória. O stager NÃO é um publicador GitHub. Nenhum motor P15 foi reconfigurado; as tentativas de upload para Drive continuam bloqueadas. Testes ainda não executados nem certificados. Não há autorização para Fase C.

PHASE_B=OPEN
CM6_TESTS=PENDING
GITHUB_PUBLISHER=NOT_IMPLEMENTED
DRIVE_HISTORICAL_WRITE=FORBIDDEN
REAL_ORDERS=FORBIDDEN
FTMO_REAL=FORBIDDEN
