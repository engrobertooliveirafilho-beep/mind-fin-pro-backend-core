# ET665.MB — Verificação independente de evidência recebida

Data: 2026-11-07. Fonte: ZIP anexado pelo operador, auditado por leitura direta dos bytes.

## Integridade
- Arquivo: `ET665_MB_FINAL_20261107_091635.zip`.
- ZIP SHA-256: `e4a60cacdf870495fd0fda921b5ee65c9b919358ebce740ed640260c1885e4e5` — corresponde ao valor reportado.
- CRC: PASS (3 arquivos: decision.json, execution.log, junit.xml).
- `decision.json` SHA-256: `4f1661afefeefbbee49e0770081f05c908793d7e1010c985c59d12f1b7e3eddd`.
- `execution.log` SHA-256: `90e8e28b7244f60963e293161920c2cc8d7bfd589a49e34b76eb720c8e9dfd32`.
- `junit.xml` SHA-256: `36d102e73514794cc170fc876860de2d9115c92173534ea02c48bf649d438432`.
- Hashes dos dois últimos arquivos conferem com `decision.json`.

## Testes
- JUnit: 50 testes, 0 falhas, 0 erros, 0 skips, 2.923 s; 2026-11-07 09:16:36 -03:00.
- Log: 50 pontos, 100%.
- JUnit contém 4 casos `test_full_engine_offline_with_synthetic_dataset` e 4 `test_drive_write_is_blocked_by_real_command_guard`, um de cada P15: p1516, p1525b, p153_p155, p156_p1510.
- Decisão local: `focused_regressions=PASS`, `p15_synthetic_end_to_end=PASS_SYNTHETIC`, `p15_integration_and_write_guard_confirmed=true`.

## Limites da certificação
- A execução é sintética/offline; não prova operações reais, conectividade com Drive, broker, desempenho de estratégias ou conformidade FTMO.
- `complete_residual_inventory=NOT_CERTIFIED`, `independent_security_approval=NOT_CERTIFIED`, `governed_github_publication=NOT_CERTIFIED` no artefato original.
- A verificação do ZIP confirma integridade e resultados reportados, não constitui revisão independente completa de segurança.
- ZIP original não publicado no GitHub; somente hashes e avaliação textual.

MB_EVIDENCE_GATE=VERIFIED_PASS
PHASE_B=BLOCKED
REAL_ORDERS=FORBIDDEN
FTMO_REAL=FORBIDDEN
