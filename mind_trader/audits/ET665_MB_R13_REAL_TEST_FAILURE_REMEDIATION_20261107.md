# ET665.MB.R13 — Real offline failure remediation

2026-11-07. User-executed offline regression evidence at commit `4d49465c6a1e8d2332959f6942b25f143eee72dd`.

## Verified user-supplied execution output
- 250 collected; 1 failure; 0 errors; 0 skipped; 249 passed.
- Failing test: `mind_trader/tests/security_review/test_et665_mb_r6_paper_fill_safety.py::test_nonfinite_result_rejected`.
- Observed: `simulate_fill(ORDER, spread=1e308, slippage=1e308)["filled"] is True`.
- Evidence ZIP: `ET665_MB_R11_20261107_195543.zip`; SHA-256 reported `5f16ac66d4ac55298e4fb3485f9f077d71472db3a64572670ad6cc6bf0d0d5cb`. Hash has not been independently recomputed by this audit.
- `focused=BLOCKED`; `phase_b=BLOCKED`.

## Root cause
The PAPER simulator checked finiteness and positivity of resulting fill price but did not reject execution costs grossly exceeding the requested entry price. For BUY, the finite expression `entry + spread/2 + slippage` can be huge yet finite and accepted. The test name mentions non-finite result, but its exact inputs expose an **unbounded cost** flaw rather than necessarily floating-point infinity.

## Patch
- `903caaf3d45560f2ba9016f2a77171102402187c`: compute aggregate execution cost, reject non-finite or `>= entry` before BUY/SELL fill.
- `2d2e0ba640c8f5ed877d7adb989e0046f7b9154d`: add three boundary regressions; preserve failing original test unchanged.
- `9db863adf378b2f8f85a45b0620ef8e776026e5a`: update consolidated expected test count from 250 to **253**.

## Gates
`R13_PATCH=PUBLISHED_UNTESTED`
`R13_RETEST=PENDING`
`PREVIOUS_RUN=249_PASS_1_FAIL`
`PHASE_B=BLOCKED`
`REAL_ORDERS=FORBIDDEN`
`FTMO_REAL=FORBIDDEN`
`MAIN_MERGE=BLOCKED`
