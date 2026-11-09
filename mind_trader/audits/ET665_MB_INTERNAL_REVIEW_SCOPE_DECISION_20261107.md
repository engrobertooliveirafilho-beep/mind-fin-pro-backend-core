# ET665.MB — Decisão de escopo: revisão interna sem auditor independente

Data: 2026-11-07. Decisão expressa do responsável pelo projeto: **não haverá revisão independente**.

## Distinção obrigatória
- `INDEPENDENT_REVIEW=WAIVED_BY_OWNER`: etapa externa retirada do plano de trabalho, **não significa PASS nem aprovação de segurança**.
- `INTERNAL_TECHNICAL_REVIEW=PARTIAL`: há inspeções históricas e remediações focadas; não há demonstração de inventário exaustivo de todas as rotas.
- `FOCUSED_TESTS=50/50_VERIFIED_PASS`: evidência ZIP SHA-256 `e4a60cacdf870495fd0fda921b5ee65c9b919358ebce740ed640260c1885e4e5`, avaliada em `ET665_MB_VERIFIED_EVIDENCE_ASSESSMENT_20261107.md`.
- `GITHUB_EVIDENCE=COMMITTED`: rastreabilidade publicada na branch de auditoria; o pacote ZIP completo não foi publicado no GitHub.
- `RELEASE_SECURITY_APPROVAL=NOT_GRANTED`: dispensa da revisão externa não autoriza merge, deploy, broker ou FTMO real.

## Inventário e gaps restantes
A matriz ET665.CM registra 12 caminhos MT5 e 6 subprocess classificados com escopo limitado. ET665.AZ registra 74 referências textuais, não uma prova de 74 rotas semanticamente auditadas. A árvore global foi truncada em levantamento anterior. ET665.BV identifica lacunas de análise de wrappers, importações dinâmicas e processos alternativos. As correções existentes e 50 testes não demonstram cobertura total.

## Política de fechamento possível
Apenas um **encerramento administrativo da macroetapa de testes** pode ser afirmado no estado atual. Um encerramento técnico da Fase B exige, no mínimo: (1) inventário residual fechado com escopo e limitações explícitos, (2) revisão técnica interna registrada no commit final com riscos aceitos ou mitigados, (3) publicação de evidências governadas e decisão explícita do proprietário. Mesmo nesse caso, o resultado será `INTERNAL_RISK_ACCEPTANCE`, **não `INDEPENDENT_SECURITY_CERTIFIED`**.

## Restrições imutáveis
`PHASE_B=OPEN`
`REAL_ORDERS=FORBIDDEN`
`FTMO_REAL=FORBIDDEN`
`MAIN_MERGE=BLOCKED`
`NO_PAID_CI`
`DRIVE_HISTORICAL=READ_ONLY`
