# ET665.MB.R2 — Revisão de dependências PAPER e correção fail-closed

Data: 2026-11-07. Inspeção autenticada de cinco fontes no GitHub, sem execução de módulos.

## Escopo e resultados
1. `app/execution/paper_broker_adapter.py`: somente simulação via `simulate_fill`; aceita parâmetros de custo manuais quando `ftmo_config_path=None`, e armazena o objeto `order` integralmente no ledger. Requer sanitização de evidências e governança do modelo de custo. Não contém chamada de envio real observada.
2. `app/execution/paper_session.py`: arquivo local de sessão, checagem de limite diário e contagem; `pre_trade_check` pressupõe estrutura válida de sessão e pode lançar exceções em JSON corrompido. Não foi alterado nesta tranche.
3. `app/execution/safe_broker_adapter.py`: identificador `broker` não-string/não-hashable podia causar TypeError na checagem de conjunto; `order` não-dict podia causar TypeError. Corrigido para rejeição explícita fail-closed na branch isolada.
4. `app/engines/core.py`: `RiskGuardian` e `FTMOGuardian` executam validações locais; `DualModeEngine` escreve ledger local, sem broker real observado.
5. `app/validation/adversarial_ai.py`: quatro revisores locais; entradas numéricas e `regime_report` malformados podem provocar exceções; dependência de `float` e operações aritméticas. Não alterado nesta tranche.

## Correção e testes preparados
- Código: commit `2993ee2072c9b6b1a1c84768f2baecd5260c1ce9` (`safe_broker_adapter.py`).
- Regressão: commit `ab98aa5e52b202dc038daba1143dc08b07203cb1` (`test_et665_mb_r2_adapter_malformed.py`), **20 casos parametrizados preparados, NÃO EXECUTADOS**.
- Evidência prévia: 50/50 PASS no commit anterior; não atribuir esse resultado à nova alteração.

## Decisão
`R2_SOURCE_REVIEW=5_PATHS`
`R2_PATCH=STAGED_UNTESTED`
`R2_TESTS=20_PREPARED_NOT_RUN`
`INVENTORY=PARTIAL`
`PHASE_B=OPEN`
`REAL_ORDERS=FORBIDDEN`
`FTMO_REAL=FORBIDDEN`
`MAIN_MERGE=BLOCKED`
