# ET665.CM.6 — Verificação independente do ZIP recebido
Data: 2026-11-07

## Evidência original
- ZIP: ET665_CM6_EVIDENCIAS.zip
- ZIP SHA-256: `8e872d2e6ab6df56d0623e9c9b131c13df645013ad752b09b4835811e91f83fc`
- ZIP CRC: PASS; três arquivos.
- JUnit SHA-256: `4804f7492e8d75556779be2a7a11e1484d9b06ab5ee9f31dcc6af7136cd630e7`
- Execution log SHA-256: `b3f363fc61420f83576b0b639aab5a098ce98c454c3e4a81afd953f4bc98ad23`
- Hash file SHA-256: `f0f8ef799f366de8b7a6de6bf0726290c21666c1d2f94b3a352f614692554d55`
- JUnit parse: tests=8, errors=0, failures=0, skipped=0, time=1.169 s, timestamp=2026-11-07T09:02:43.156436-03:00.
- JUnit hash coincidente com manifesto interno e resultado local informado.
- Arquivos textuais originais publicados em `mind_trader/audits/ET665_CM6_EVIDENCE_20261107/`; ZIP binário não publicado.

## Conclusão e limites
CM6 focused regression artifact gate PASS; CM4 10/10 + CM5 9/9 + CM6 8/8 = 27/27 focused PASS. O stager não publica no GitHub; varredura de segredos é heurística e requer revisão humana. Os motores P15 não estão integrados ao stager. Aprovação formal de segurança, inventário residual completo e governança de exportação seguem pendentes. Nenhuma autorização para Fase C ou operações reais.

CM6_ARTIFACT_GATE=PASS
PHASE_B=OPEN
REAL_ORDERS=FORBIDDEN
FTMO_REAL=FORBIDDEN
