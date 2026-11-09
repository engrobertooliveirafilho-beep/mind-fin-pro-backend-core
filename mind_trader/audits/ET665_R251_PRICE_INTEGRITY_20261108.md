# ET665.R251 — Price integrity fail-closed

Date: 2026-11-08. Source inspected: P15.25 research loader in draft PR #18.

## Finding
The prior helper `f(v)` silently converted invalid numeric strings to `0.0`; `float("nan")` and infinities were accepted. As a result, invalid dataset values could be skipped or contaminate research metrics rather than being rejected.

## Change
The helper now rejects malformed, missing and nonfinite values with `ValueError`. This is a fail-closed change and may expose invalid historical CSV files previously ignored. It does not validate every downstream arithmetic operation.

## Tests
Published four unittest methods: nonfinite rejection, invalid rejection, valid finite control, and malformed CSV rejection. **NOT EXECUTED**; no CI, Docker, JUnit or independent approval evidence.

## Limits
No merge or production change; PR remains draft. FASE_B=0/16 | HP19=0/19 | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN | COST=R$0.
