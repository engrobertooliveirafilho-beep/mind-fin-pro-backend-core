# ET665 — P2383 original P2380 population walk-forward evidence

Date: 2026-11-22
Repository: `engrobertooliveirafilho-beep/mind-fin-pro-backend-core`
Base branch: `main` (PR #37 remains draft; no merge)
Working branch: `engineering/et665-realdna-reconciliation-20261121`
PR base HEAD: `10b778d64f479698a866774328e306ad704cc77b`

## Original Drive source recovered
- P2380 folder: `1rVmxHZJwh47fvIW03t_efE6BIana50ot`
- Canonical feedback CSV: `de40_forward_paper_feedback_all.csv`
- Drive file ID: `1djqqQ7NrpM-uQRYrPU0uB9BHpdOhUZbQ`
- Bytes: 261,383
- SHA-256: `31aa0c813150b249aa6c653971dbb5f9766b6905c642807e81796d455bd4c197`
- Rows: 500; unique signal IDs: 500; distinct entry timestamps: 499.
- All 500 rows are PAPER_ONLY, REAL_ORDERS=FORBIDDEN, FTMO_REAL=FORBIDDEN and carry `PAPER_FEEDBACK_PROXY_NOT_REAL_PNL`.
- Historical P2380 metrics reconcile to 243 positive, 254 negative, 3 zero; expectancy -0.083805 R; PF 0.832504. These are proxy outcomes, not actual broker fills or realized live PnL.

## P2383 exact contract executed on the original population
- Existing `app/runtime/p2383_walk_forward_contract.py` and existing 8-test suite were read from PR #37 HEAD and executed in an isolated Python harness.
- New source-backed integration test added: `tests/test_p2383_original_drive_population.py`. It requires the Drive CSV to be provided through `P2380_FEEDBACK_CSV`, verifies the exact SHA-256, source safety flags, full 500-row population and all five strict chronological folds.
- Execution: **9/9 PASS**, 0 failures, 0.03 seconds. The 9 tests are 8 existing contract tests plus 1 original-Drive integration test.
- Five expanding folds: initial train 250; test windows 50 each. Boundaries:
  1. train ends 2025-06-17 15:00; test ends 2026-01-05 10:00.
  2. train ends 2026-01-05 10:00; test starts 2026-01-05 18:45; ends 2026-03-20 01:45.
  3. train ends 2026-03-20 01:45; test starts 2026-03-20 04:40; ends 2026-04-22 22:16.
  4. train ends 2026-04-22 22:16; test starts 2026-04-23 12:30; ends 2026-05-21 19:21.
  5. train ends 2026-05-21 19:21; test starts 2026-05-22 05:20; ends 2026-06-23 06:02.
- Fold-level proxy diagnostics (not strategy certification): F1 28W/22L, expectancy -0.119447 R, PF 0.728529; F2 30W/20L, +0.148891 R, PF 1.372228; F3 22W/28L, -0.199884 R, PF 0.643065; F4 20W/30L, -0.163096 R, PF 0.718972; F5 29W/21L, +0.094365 R, PF 1.224679.
- One duplicate timestamp exists in the population, but no fold boundary splits equal timestamps; all five train/test boundaries are strictly chronological.

## Material leakage confirmed in P2381/P2382
- P2381 output folder: `1unpqgP-L2HwcAdqHhGMrJ7UgtFTN0Tzt`; patched candidates CSV: `1Aa5a9cRWGlTBCwkWa_TeArS7yExd4S46`; loss memory graph: `1HD74aroxPSZ4oWUBXUAKGt5FAbPRWE`.
- P2381 produced 254 loss-memory nodes and selected 227 replay candidates using the full 500-row outcome population.
- Of the 227 selected candidates, 117 fall in P2383's future/test half (not available to a train-only selection process): F1=26, F2=28, F3=20, F4=18, F5=25.
- Every one of those 117 selected future rows has positive `realized_r`; this directly explains why P2382's 224W/0L result is selection-contaminated. P2382's survivors remain diagnostic only and are not used as P2383 input.
- P2381 original engine source was not recovered in this pass; only its outputs and run log were found. Therefore fold-specific train-only loss-memory regeneration is still blocked and no P2381 patch is applied to test windows.

## Certification boundary / next
- P2383 chronological split: **executed against canonical 500-row Drive CSV**.
- Performance: **NOT CERTIFIED**; outcomes are explicitly proxy PnL and no actual broker fill ledger is present.
- P2381 train-only patch replay: **BLOCKED** until original P2381 engine source and dependencies are recovered or a separately specified replacement is approved.
- No strategy promotion, broker execution, MT5 consumption claim, merge, production change, or paid service.
- Main intact; PAPER_ONLY; REAL_ORDERS and FTMO_REAL forbidden; Drive originals read-only; cost R$0.

`P2383_ORIGINAL_POPULATION=500 | SHA256_VERIFIED | WALK_FORWARD=5_FOLDS | TESTS=9/9_PASS | P2381_TRAIN_ONLY_REPLAY=BLOCKED | PERFORMANCE_CERTIFIED=FALSE | MAIN=INTACTA | PRODUCTION=INTACTA | COST=R$0`


## Historical P2383 run invalidated by source reconciliation
- Original Drive folder: `1zyXXpoQyDj10MbwIJOprF1L46HMPnVMQ`; original summary `1ZqZcg-pr_PFEcCjyljopMsY_3w80NcQn`; windows CSV `1jb7poNcZ4_n-xVo5whhsY1BsWabvf06P`.
- The historical P2383 run consumed the P2382 output (227 selected rows), not the complete P2380 population. Its own summary flags `P2382 may contain survivorship bias`.
- Its five recorded windows are not a valid monotonic chronological partition: window 1 start 2025-05-12 > end 2025-04-22; window 3 start 2025-09-30 > end 2022-10-12; window 5 start 2026-04-07 > end 2025-03-06. Window 2 begins 2022-08-18 after the purported first window, and window 4 begins 2022-11-10 before window 2 ends 2025-10-31. Therefore the old `chronological_5_window_walk_forward` label is unsupported by its window ledger.
- Historical run recorded 227 groups, 227 rejected, 0 promoted, 0 observed. It must not be used as proof of walk-forward validation.
- The new P2383 execution in this audit supersedes that run's population/split methodology only: complete P2380 CSV, SHA-256 verified, 250-row initial train, five strict future windows. It still does not certify edge performance or permit promotion.


## 2026-11-21 hardening follow-up (isolated verification)
- Hardened `app/runtime/p2383_walk_forward_contract.py`: reject partial safety metadata; reject any LIVE/allowed real orders/FTMO or real-PnL warning when canonical safety fields exist; reject equal timestamps across train/test and test/test boundaries.
- Seven new regression cases added to `tests/test_p2383_walk_forward_contract.py` (1 partial safety, 4 unsafe fields, 1 boundary tie, 1 internal tie).
- Verified in an isolated local Python reconstruction of the published module and its 15 unit-test cases: `python -m pytest -q tests/test_contract.py` => **15 passed in 0.06s**. This is a manually transcribed isolated mirror, NOT an authenticated Git checkout test and NOT original-Drive integration reexecution.
- Original Drive integration test `tests/test_p2383_original_drive_population.py` remains unexecuted in this follow-up; no P2381 source code recovered, no train-only replay, no performance certification.
- GitHub published source commit `92cd5f8f7024bb8037b029cc6d62afd6b65bac8d`; regression commit `508d0c25dfcfb150a89a973a322ba4d8d20bab3a`.
- Scope: PAPER_ONLY; no merge, production, real orders, FTMO real, or paid infrastructure.


## Additional fail-closed audit (2026-11-21)
- Found a remaining bypass: the prior safety check accepted a mixed population where one row declared the canonical PAPER safety fields and the other 499 omitted them. Such a population could be accepted despite unverifiable source mode.
- Found an exception-handling defect: unhashable `signal_id` values such as lists or dictionaries could raise `TypeError` rather than the intended deterministic `ValueError`.
- Fixed `chronological_folds` to require consistent safety-field presence across all 500 rows and nonblank string signal IDs.
- Added 6 regression cases: one mixed-schema case and five malformed-ID cases.
- GitHub commits: source `3bb317580c755321cb21dd80f7b7ebba20b93b08`; tests `33dfe4325a5f8b0c2a2180649aaeb84a2f6c6fa1`.
- **Verification boundary:** changes published, but the 6 new regression cases have NOT been executed in this pass. The previous 15/15 isolated tests do not certify the new changes. Raw GitHub checkout from this execution environment was unavailable (DNS failure), so a clean-checkout test is still pending.
- P2381 original source still not recovered: Drive search located P2381 output folder, run log and historical test-output folders, but no executable source. Do not infer engine implementation from folder names or historical `CERTIFIED` labels.
- No performance certification, strategy promotion, merge, real orders, production changes or cost.


### Additional isolated logic verification
- Executed the six new negative cases in an independent Python harness reproducing the new validation logic: **6/6 PASS**.
- This verifies only the extracted guard logic, NOT the published module in an authenticated checkout and NOT the entire P2383 test suite. Historical original-CSV integration is not reexecuted in this pass.


## 2026-11-21 strict PAPER-only and original CSV revalidation
- Found a remaining fail-open gap: 500-row populations with *no* PAPER-only metadata were previously accepted because the earlier code supported legacy synthetic fixtures.
- Corrected P2383 to require all four safety fields on every row: `mode=PAPER_ONLY`, `real_orders=FORBIDDEN`, `ftmo_real=FORBIDDEN`, `warning=PAPER_FEEDBACK_PROXY_NOT_REAL_PNL`. Missing, partial, mixed or unsafe fields fail closed.
- Updated synthetic unit fixtures to carry canonical PAPER safety fields and added a metadata-free-population rejection test.
- **Actual isolated Python execution** in local reconstructed files: `P2380_FEEDBACK_CSV=/mnt/data/de40_forward_paper_feedback_all.csv PYTHONPATH=/mnt/data/p2383_validation pytest -q /mnt/data/p2383_validation/tests/test_contract.py /mnt/data/p2383_validation/tests/test_original.py` => **23 passed in 0.08s** (22 unit cases plus 1 original-Drive CSV integration).
- Original Drive CSV SHA-256 verified: `31aa0c813150b249aa6c653971dbb5f9766b6905c642807e81796d455bd4c197`, 500 rows, five chronological folds of 50 test rows, strict boundaries.
- The executed files are locally reconstructed from connector-read GitHub source and test text, **not a clean authenticated Git checkout**. Thus isolated contract/data integration is PASS, repository checkout CI/E2E remains uncertified.
- GitHub commits: strict safety source `83ace1b6e4fdf54350cd3a054867337576286477`; updated tests `ff3e809c0ac59313810d0019c4a7de4a7688d328`.
- P2381 engine original source not recovered; P2381/P2382 survivor selection remains blocked from strategy promotion. PAPER_ONLY; MAIN and production intact; no orders or cost.


## Cross-project Drive recovery: MIND agents and STEP 520
- Re-read canonical registry from Drive file `1IGBrD8FL3CLfVMngnG0rA765KlaZKfoD`: 81 agent records, 81 unique IDs, 412 STEP references covering 166 distinct STEP IDs, 50 agents with no step_ids, 52 with `active=true`, 81 with `auto_run=true`, 26 with `governance_rules.human_approval_required=true`. These are **catalog flags only**, not verified executable agent health or authorization.
- Re-read STEP520 source Drive file `1ijSuxuIXJFlX8M5KrfMgVgoUQiACQ90-`: original `ComplianceEngine.check` explicitly returns `allowed=True` for any action not listed in `blocked_actions`. Original test `1obWpiLt-x4U6puExfxPQu-ENWos-nBBL` expects an arbitrary `qualquer_coisa` action to pass. This is fail-open and cannot be treated as a secure compliance gate.
- Do not wire STEP520 original to PAPER gateway or agent execution. A separate default-deny remediation and independent approval-verifier contract are required before runtime certification.
- P2381 original executable code remains unrecovered; no claim that catalog flags or historical log `CERTIFIED` imply working engines.


## STEP520 original recovery and functional hardening (2026-11-21)
- Recovered original STEP520 `app/compliance.py` from Drive `1ijSuxuIXJFlX8M5KrfMgVgoUQiACQ90-` and original tests from `1obWpiLt-x4U6puExfxPQu-ENWos-nBBL`.
- Original behavior was fail-open: arbitrary `qualquer_coisa` passed; the original test asserted this. It is intentionally NOT preserved for the PAPER gateway.
- Published `app/compliance.py` (source commit `5c573b941aa139b1a71c9995a5e4a3e9a5b9c69c`) and `tests/test_step520_paper_compliance.py` (test commit `7399ec2f99295a65cc989134004b38c3c1fd8a0d`) on existing isolated PR branch.
- Default deny, explicit PAPER action allowlist, invariant real-order prohibition and required PAPER safety flags. No production route or order broker wired.
- **27/27 PASS, 0.05 s** in local isolated Python harness `/mnt/data/step520_validation`, with reconstructed source matching functional logic. Direct GitHub raw checkout unavailable due DNS/network error. This does NOT certify clean checkout or E2E.
- GitHub readback verified source and tests exist on branch; MAIN/production unchanged; originals read-only; no paid services.
- Further action: integrate only with proven PAPER gateway once its canonical source and tests are recovered; never treat STEP520 as a live-trading authorization layer.


## STEP520 adversarial policy escalation fix (2026-11-21)
- Discovered that custom policy `allowed_actions` could authorize arbitrary actions (e.g. `send_trade`, `broker_send`) because the prior hardening only banned a fixed list/prefix of real-order action names. Custom policy values with malformed entries were also insufficiently validated.
- Corrected original-recovered `app/compliance.py` on isolated PR branch: enforce a fixed canonical set `paper_feedback/paper_replay/paper_validate` independent of custom policy, reject whitespace/noncanonical actions, reject malformed allow/block lists and non-string entries.
- Added nine parametrized regression cases in `tests/test_step520_paper_compliance.py` (5 custom action escalation, 4 malformed policies).
- Commits: source `0f33144290e4f1eada2eec24f7b9325a0c2eea27`, tests `8dfe4eec51a91d63f570156b5e03e27cfda508df`, normalization correction `7428da34d57ca4fc5705b984688e5f9c3f8387d2`.
- **Execution evidence:** 12/12 independent adversarial policy logic checks PASS in Python. The published module's full pytest suite was **not executed in this turn**. Do not conflate independent checks with checked-out source regression certification.
- Google Drive searches for `gateway_paper.py`, `paper_execution_gateway`, `test_paper_gateway` returned no direct file matches; this does not prove nonexistence across all Drive/GitHub histories. No gateway integration performed.
- MAIN/production intact; PAPER_ONLY; REAL_ORDERS and FTMO_REAL forbidden; no promotion, merge or paid service.
