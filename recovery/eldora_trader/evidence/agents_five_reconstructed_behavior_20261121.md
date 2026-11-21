# Integração PAPER — cinco agentes históricos (2026-11-21)

## Evidência executada

Comando: `python -m unittest discover -s tests -v`, Python offline em diretório temporário isolado.

Resultado: **10/10 PASS**, 0 FAIL, 0.001 s. SHA-256 do log: `fc84fda1471687d14590266b76ad6f6b6b53e000a9c27bbe6b5d7776ddcbfc5e`.

**Limitação material:** O ambiente local utilizou **reproduções manuais reduzidas** dos cinco agentes (mesmos AGENT_ID, STEP_IDS e respostas stub observadas no Drive), e uma reprodução do dispatcher restrita aos cinco IDs. **Não** foram executados os arquivos byte-identical do GitHub. Portanto, o resultado é uma **verificação de comportamento de referência**, não uma certificação de integração dos fontes originais.

Fontes originais publicados, sem alteração de semântica:
- `app/agents/sec_sentinel.py` (Drive `1B4RdoylWbUMmpUmk1JGzylu0Yh-gtaEW`)
- `app/agents/sec_gatekeeper.py` (Drive `15--U6Liy5Jr7kR2ktsBMlD7SswZBKR8P`)
- `app/agents/domain_economics_finance_markets.py` (Drive `1NWZNHcOxAvhVvS3RFNDvhWQeG4KLqdFx`)
- `app/agents/core_safety_compliance_hub.py` (Drive `1uH27Ze9FOz1xg05jqidLKiCDy7drj3X2`)
- `app/agents/dev_test_guardian_agent.py` (Drive `10Uu_8GhAd_Fido4fZMMkx1BDjPRERvho`)

Escopo: preservar a distinção entre fonte recuperado e implementação funcional; nenhum desses cinco agentes pode ser promovido.

`MAIN=INTACTA | PAPER_ONLY=TRUE | E2E_CERTIFIED=FALSE | COST=R$0`
