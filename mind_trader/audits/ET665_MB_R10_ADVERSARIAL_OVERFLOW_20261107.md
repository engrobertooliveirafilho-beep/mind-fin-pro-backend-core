# ET665.MB.R10 — Overflow de cálculos adversariais e gate consolidado

Data: 2026-11-07. Inspeção de código e publicação autenticada no GitHub; nenhum teste foi executado nesta etapa.

## Achado
A validação R9 verificava `math.isfinite` em campos individuais, mas não em resultados intermediários. A diferença `target-entry`, `entry-stop`, soma `open_risk+risk_amount` e produto `risk_amount*1.25` podiam transbordar para infinito mesmo com operandos finitos, comprometendo as análises adversariais.

## Correção
- `bc1a0fdbda9e01519be5c0968dee581c84907ee6`: veto preventivo a resultados intermediários não finitos.
- `e52c388b9281df13bded62fbd5345083681cc18c`: três testes parametrizados adicionais para overflow; **não executados**.
- `8abf12b201f7fc0a3c23ddba2837220008cc013f`: runner consolidado atualizado de 224 para **227** casos esperados.

## Situação
- 50 testes históricos anteriormente aprovados em revisão anterior, não reexecutados após os patches.
- 177 regressões novas R2–R10 preparadas, ainda não executadas.
- 227 testes consolidados aguardam execução offline isolada com JUnit e SHA-256.
- Auditoria de rotas residuais permanece parcial; testes positivos não implicam aprovação de segurança nem autorização real.

`R10_PATCH=PUBLISHED_UNTESTED`
`CONSOLIDATED_TESTS=227_EXPECTED_NOT_EXECUTED`
`PHASE_B=OPEN`
`REAL_ORDERS=FORBIDDEN`
`FTMO_REAL=FORBIDDEN`
`MAIN_MERGE=BLOCKED`
