# ET665.MB.R3 — Regras FTMO: inspeção e hardening PAPER

Data: 2026-11-07. Inspeção autenticada de `ftmo_ruleset.py`, `paper_broker_adapter.py` e regressões históricas. Não foi executado pytest, CI, MT5 ou broker.

## Achado
`validate_ftmo_config` pressupunha objeto dict; JSON `null`, lista e tipos incompatíveis podiam lançar exceção. Valores `NaN`, infinitos e bool eram aceitos pelo controle de tipo numérico em determinadas chaves. `load_ftmo_config` não convertia falha de parsing/arquivo em decisão de bloqueio.

## Remediação
- Commit `c21e8dcd0b3fed1e0b9a1a1eef84383f5daea4f2`: rejeita config não-dict, valores numéricos não finitos/bool e falhas de leitura/parsing como `valid=False`.
- Commit `b0f26972a617ccada94b48e7b0e69f658b454068`: **42 testes preparados e NÃO EXECUTADOS** (5 tipos inválidos + 32 combinações numéricas + 4 arquivos corrompidos + 1 caso positivo).
- O teste `test_et665_mb_r2_adapter_malformed.py` da etapa anterior tem 20 casos também não executados. **Não associar 50/50 PASS anterior a commits R2/R3.**

## Pendências de revisão
- `audit_rule_application` persiste o objeto `trade` completo no arquivo local; revisar minimização de dados antes de publicação.
- `paper_broker_adapter` permite custos manuais sem config FTMO em chamadas diretas; no gateway inspecionado, o caminho PAPER fornece `ftmo_config_path`.
- A revisão do grafo transitivo de importações, wrappers, demais rotas e inventário original de 74 referências segue parcial.
- Esta etapa não modifica main nem autoriza ordens reais.

`R3_PATCH=STAGED_UNTESTED`
`R3_REGRESSIONS=42_PREPARED_NOT_EXECUTED`
`PHASE_B=OPEN`
`REAL_ORDERS=FORBIDDEN`
`FTMO_REAL=FORBIDDEN`
