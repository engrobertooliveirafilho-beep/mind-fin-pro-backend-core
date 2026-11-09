# ET665.CM.5 — Evidência recebida e auditada
Data: 2026-11-07

Pacote recebido: ET665_CM5_EVIDENCIAS.zip
- ZIP SHA256: 749f3627af80ba6871b0105b10e8562f6a3afd70c2fe4b0783d1b82f43274f13
- JUnit SHA256: 6f6cc36b528dd61bfd045004823fda8a2575af515291cd9aacc58ac7c3bbcce2
- Log SHA256: 55cf85556f9212aec3cf3688ddb048b901ad2536966113215358784c657a7532
- Hash file SHA256: 0608e3a92f535036dcac762d37178849ff5308ada7070d7adae453a7e461a05c
- ZIP CRC: PASS
- XML: parse válido; tests=9, errors=0, failures=0, skipped=0, time=0.533 s; timestamp 2026-11-07T08:46:12.413247-03:00
- SHA do JUnit coincide com registro do operador e arquivo interno.
- Arquivos de evidência textuais publicados em mind_trader/audits/ET665_CM5_EVIDENCE_20261107/; ZIP binário não publicado.
- CM4: 10/10 PASS; CM5: 9/9 PASS; 19/19 testes focados em duas execuções.

## Limites de certificação
Os testes CM5 verificam bloqueios estruturais via AST. Não certificam todas as rotas MT5, nem comportamento de integração com terminal. A exportação governada dos motores P15 permanece não implementada e sem testes. Não executar suíte histórica nem modificar Drive histórico.

CM5_ARTIFACT_GATE=PASS
PHASE_B=OPEN
GOVERNED_EXPORT_GATE=PENDING
SECURITY_APPROVAL=NOT_GRANTED
REAL_ORDERS=FORBIDDEN
FTMO_REAL=FORBIDDEN
