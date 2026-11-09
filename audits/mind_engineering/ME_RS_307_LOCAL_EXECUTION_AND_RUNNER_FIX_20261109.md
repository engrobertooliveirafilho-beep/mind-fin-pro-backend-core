# ME-RS-307 — Reproducible local regression and runner correction

Date: 2026-11-09. Scope: isolated synthetic POST_R6 reconstruction, NOT historical certification.

- Executed: `python /mnt/data/me_rs306/tools/run_me_rs_307_offline.py --output /mnt/data/ME_RS_307_EVIDENCE.json`.
- Actual output: `PASS_SYNTHETIC`; **10/10 tests PASS**, 0 failures, 0 errors, exit code 0.
- Local monitored module SHA256 before/after: `c185004a4d7e555d5e54ac71144792051f2195915c59906e5612f85b42547397`.
- Local test suite SHA256 before/after: `c66c7a0fc5bb0d663b2c495c89d5b9911b715e7b2c8aef2d502be5d1b770b0b1`.
- The local reconstruction is not byte-for-byte authenticated against GitHub; local test suite is `tests/test_post_r6.py`, not GitHub's `tests/test_me_rs_303_post_r6_offline.py`.
- Corrected the GitHub `tools/run_me_rs_305_offline.py` test-result parser to require an exact ten-test success result rather than substring matching. This correction is **published but has not been executed in an authenticated checkout**.
- Historical 2,513 rows NOT processed; original R8 11/32 NOT recovered; R4–R8 parallel NOT_RUN; no production, main, merge or Drive mutation.

Decision: **SYNTHETIC PASS / HISTORICAL BLOCKED / PARALLEL NOT CERTIFIED**.
