# ET665.CM.7 — Verificação independente do ZIP recebido

Data: 2026-11-07

- ZIP: `ET665_CM7_EVIDENCIAS.zip`.
- ZIP SHA-256: `e4e2912343cc030f5b89606abdd0aee2b8e028df6314ad510b2568441189069f`.
- CRC: PASS, três arquivos.
- JUnit SHA-256: `476423bbf7092b4e1875eb20c85e8aafa83079de03042b73dec7964386b1eb79`.
- Log SHA-256: `1c4e0c4945ea268c3bc11a7a613907555ed512b9eeaf46afe02b9e771b929bcc`.
- Hash file SHA-256: `1bdbe9537660fbca2b180867462b15448297905da7c26d887cc7a1e316f23fc7`.
- JUnit: 15 tests, 0 failures, 0 errors, 0 skipped, duration 1.105 s; timestamp `2026-11-07T09:09:11.811060-03:00`.
- Manifest interno corresponde ao SHA-256 calculado do JUnit.
- CM4 10 + CM5 9 + CM6 8 + CM7 15 = 42 testes focados aprovados em execuções distintas.

Limitações: regressões estruturais/comportamentais não constituem execução ponta a ponta dos quatro motores P15. O ZIP original não é armazenado neste repositório; evidência de integridade documentada. Revisão formal de segurança e Fase B permanecem abertas.

CM7_ARTIFACT_GATE=PASS
PHASE_B=OPEN
REAL_ORDERS=FORBIDDEN
FTMO_REAL=FORBIDDEN
