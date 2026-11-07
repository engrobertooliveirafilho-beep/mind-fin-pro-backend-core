# ET665.MB.R19 — R18 pytest collection failure, source correction

Date: 2026-11-07.

## Observed user execution
- Checked-out source: `4763f970a9fd32d3ca31e7f1bb493c06f4333aba`.
- Test runner stopped during collection with Python `SyntaxError: unexpected character after line continuation character` at `mind_trader/app/p69_73_mt5_ftmo_demo_governor/engine.py:63`.
- JUnit reported `tests=1`, `errors=1`, `pytest_exit_code=2`. **Not a completed 264-test run**.
- User-reported failed-run ZIP: `ET665_R18_20261107_200236.zip`; SHA-256 `2224fbbd935da33cae209987f34c968cf65ee71e07d1c5beb982891bc15cb315`.

## Root cause and correction
The R18 patch accidentally inserted literal backslash-n sequences in Python source rather than newlines. The affected block contained malformed `risk_valid` and `allow` expressions.

Fix commit `31b28c30549d2987eb366703e49db32956f22194` replaces that block with correctly formatted Python expressions, preserves DEMO-only, positive finite numeric risk validation, and removes a duplicate `risk_valid` condition.

## Validation boundary
Source correction was published to the isolated PR branch. No local or remote Python execution is claimed for the corrected commit. The full 264-case offline suite **must be rerun**; until then `R19=PATCH_PUBLISHED_UNTESTED`, `PHASE_B=BLOCKED`, `REAL_ORDERS=FORBIDDEN`, `FTMO_REAL=FORBIDDEN`, `MAIN_MERGE=BLOCKED`.
