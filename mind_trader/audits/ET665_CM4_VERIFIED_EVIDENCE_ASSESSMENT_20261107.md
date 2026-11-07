# ET665.CM.4 — Parecer de evidências (2026-11-07)

## Evidências recebidas e verificadas
Arquivo fornecido: ET665_CM4_EVIDENCIAS.zip.
- ZIP SHA-256: e82a89c0809d84f9f1b43c05a4ecdd1f255178faef92dd3f7f37b471e8724fce.
- JUnit SHA-256: 311ecc81207efe01d394c19f21f1b8e4a89f3c85d6aae45b0fa0e2856879a857.
- Log SHA-256: 3a7595f1ed0b8ce91ff11c8a9ea43bcec9d3221574c06e918523636cb091325a.
- Hash record SHA-256: f1b6e33d9ecce7cdcc6b24d437086d4c72dd264bf9fe34d422404fbfcfda3512.
- SHA-256 JUnit coincide com valor do arquivo et665-cm3-sha256.txt; XML parse válido.
- XML testsuite: tests=10; failures=0; errors=0; skipped=0; time=0.674 s.
- Timestamp no JUnit: 2026-11-07T08:32:51.557229-03:00.
- Arquivos textuais JUnit/log/hash publicados em mind_trader/audits/ET665_CM4_EVIDENCE_20261107/.
- ZIP binário original não publicado pelo conector de texto. Sem alteração da suíte histórica.

## Confronto com matriz de riscos
- P15.16, P15.25B, P15.3–P15.5 e P15.6–P15.10: 8 testes locais PASS, apenas escopo do helper rclone e cleanup.
- P77B e P79: 2 testes locais PASS de AST para bloqueio inicial; NÃO equivalem a testes de conexão MT5.
- P77, P13.8/P13.9, P1505b, P1804/P1805, P76A/P76A2/P76B: isolamento ainda não certificado.
- Destino governado de exportação separado do Drive histórico ainda pendente.
- Ledger Drive e parecer formal global ainda pendentes.
- CI GitHub sem execução confirmada. Não repetir 99/99 históricos.

## Decisão
CM4_LOCAL_EVIDENCE_GATE=PASS
PHASE_B=OPEN
SECURITY_APPROVAL=NOT_GRANTED
REAL_ORDERS=FORBIDDEN
FTMO_REAL=FORBIDDEN
NO_MAIN_MERGE
