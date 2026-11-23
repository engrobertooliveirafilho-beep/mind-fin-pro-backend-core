# R822 — Historical P4.72B test evidence recovered
Date: 2026-11-22

## Drive sources
Read two independently indexed `pytest_p472b.txt` records:
- Google Drive ID `1O4Cr3Lcpnq-XGNrxtlLrDQwOU0xcG3P-`
- Google Drive ID `1BbKNfo6mh4CkaJZtAvz2YxRAa7NyCT_q`

Both logs report `.. [100%]` for two historical tests in `tests/test_p472b_capability_recovery_bridge.py`:
- `test_p472b_capability_bridge_imports_top5`
- `test_p472b_capability_bridge_has_successful_call`

Both logs contain RuntimeWarning `coroutine 'memory' was never awaited` and `coroutine 'memory_runtime' was never awaited` associated with the two tests. Each log shows four warning entries (two warnings per test), with Python 3.12 Windows pytest paths. This is historical evidence of 2 test passes with unresolved asynchronous runtime warnings, not evidence of functional certification.

Historical test *source* IDs remain unresolved/unreadable: `1ZRQFF1Pvepn0T0M4W1qXwkMQ6m-qqt8D`, `1qQyIW9xbG5MB5qOGYaODi5Dh1LYzcb-L`, `1qFoCHFG2vPIXgo2NdeJjJGCm4lfdwTXE`. Do not infer assertions or exact code from filenames/logs.

## Current state
R815–R817 isolate and block active imports/function calls in capability recovery; R818–R820 regressions; R821 historical code map recovered. No previously completed step rerun. The historical test expected imports and successful calls, which are not valid requirements for the newly hardened declared-only inspection. Do not restore unsafe probing to satisfy old tests.

## Limits
Drive logs recovered and compared. No new Python execution in R822, no current consumer audit, no runtime E2E, no merge or production mutation.
`R822=HISTORICAL_LOGS_2/2_RECOVERED | HISTORICAL_TESTS_2_PASS_WITH_WARNINGS | CURRENT_E2E=FALSE | MAIN=INTACT | COST=R$0`
