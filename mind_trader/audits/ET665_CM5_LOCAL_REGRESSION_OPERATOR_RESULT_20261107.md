# ET665.CM.5 — Execução local reportada (2026-11-07)

O operador executou `python -m pytest -q mind_trader/tests/test_et665_cm5_mt5_fail_closed.py --junitxml=et665-cm5-junit.xml` após atualizar seletivamente os arquivos da branch de auditoria. Saída compartilhada:

```text
.........                                                                [100%]
ET665_CM5_EXIT_CODE=0
```

- CM5: 9/9 PASS reportados pelo operador.
- CM4: 10/10 PASS, evidência JUnit e hash previamente verificados.
- Total regressões focadas: 19/19 PASS reportados, em duas execuções distintas.
- CM5 JUnit, log e hash ainda não recebidos; hash independente e upload pendentes.
- Suíte histórica preservada, sem reexecução nesta etapa.
- Exportação P15 para Drive histórico continua bloqueada; adaptador governado não implementado.
- Não houve certificação de conectividade MT5 nem autorização de operações reais.

PHASE_B=OPEN
CM5_ARTIFACT_GATE=PENDING
GOVERNED_EXPORT_GATE=PENDING
SECURITY_APPROVAL=NOT_GRANTED
REAL_ORDERS=FORBIDDEN
FTMO_REAL=FORBIDDEN
