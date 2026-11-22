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


## ET-019: original FTMO ExecutionV4 recovered and stale-mark remediation
- Read Drive canonical remediation ledger `1WYqMJ-wzqmDWTaRzwJGFk4Hj4b7MuBNR7m0F9ct99mI`: ET-019 identified potential sequential-close stale mark.
- Recovered actual `ftmo_execution_v4.py` Drive file `1PUorE7pvNKMNKNNoqUJ07l73jPgB-vgD`, original `test_execution_v4.py` `1ZUiegiL4HKf72wp9OuOC0cnK2vlTT3K7`, and original V5 dependency copies `portfolio_runtime.py` `1Oy1Si3--NtCJPpo2FYqCckYrN0b2Fbqd`, `ftmo_pretrade_v2.py` `1qqfIh-m-SciCThEyk2p5bSLmL75vpTLR`, `ftmo_paper_guard.py` `1ugE_FFCfZPeSNJZmcxCxRJcNpFsd2QLk`.
- Original V4 SHA256 verified locally: `32ec8af253054f0d44c1daac6579e4d55b247c6de9f565c54009f596f3ace365`. Portfolio SHA256 verified `dce707f6727560fa3b89181276e977109b69831b32ad11ae587b9643008ed4fa`.
- Baseline 8/8 PASS offline using actual original Drive files. Remediated V4 marks all current bar prices (exit prices for exiting positions, close for survivors) in one full portfolio snapshot before calling sequential `close()`.
- After patch, **10/10 PASS** (8 original V4 tests + 2 adversarial tests), `python -m unittest -v test_execution_v4 test_execution_v4_atomic`, local `/mnt/data/et_v4_lab`, 0.002 s. No real orders.
- Published recovered/patched source `app/runtime/ftmo_execution_v4.py` commit `bc81023e95f68245b5abc3076ca7611334b27471`; new tests `tests/test_ftmo_execution_v4_atomic.py` commit `a2652bd6bfac7a0372a8ffc73717b21f22defd4a`.
- **Scope limit:** Tests executed with original Drive module at top-level in isolated staging; GitHub module is under `app.runtime` and its external original dependencies have not yet been published or integrated into canonical package. No clean-checkout CI or E2E certification. Source recovered and behavioral fix PASS offline; integration pending.


## FTMO ExecutionV5 recovery / input validation (2026-11-22)
- Drive EXECUTION_V5 folder `1jRNxehoemCaRppPcQHMbR2J9S3wCj5fl`; recovered original `ftmo_execution_v5.py` file `1Bk-gkLSKK2d2k4DawfhcGLYdOTjSTlcW`, V4 and dependencies (see ET-019). Original SHA256 `644df62eb0289a6bcce83113d78d316255d6e6862c2a06c077b440d017fce2f4` from original V5 manifest `1DcBiBsQAGvbWd-sgB-c--9K6U--2j732`.
- Published `app/runtime/ftmo_execution_v5.py` commit `0ecb01dae3d40bb5c1ee735493968f0e33247252`; `tests/test_ftmo_execution_v5_rollover.py` commit `1d49ac53811d6a4da1b5e4902bbecf18dfed57d7`.
- Fix: prevalidate OHLC, day type and chronology before `new_day`; invalid input does not mutate day. Source was reconstructed from original Drive V5, not a byte-identical copy.
- Local isolated harness `/mnt/data/eldora_v5_validation` with original Drive dependencies: **5/5 PASS** for invalid bar, missing target, invalid day, valid rollover and reversal. These tests exercised a manually reconstructed local V5 implementation, not a GitHub clean checkout.
- Original V4 Drive regression independently rerun in this turn: **8/8 PASS** `python -m unittest -q test_execution_v4` with original Drive files.
- No broker calls, real orders, production deployment or main merge. Full V4/V5 dependency packaging and end-to-end tests remain pending; E2E_CERTIFIED=FALSE.


## FTMO PAPER V2/V3/V4/V5 package integration (2026-11-22)
- Recovered from Drive V5 folder `1jRNxehoemCaRppPcQHMbR2J9S3wCj5fl`: `ftmo_paper_guard.py` ID `1ugE_FFCfZPeSNJZmcxCxRJcNpFsd2QLk`, `ftmo_pretrade_v2.py` ID `1qqfIh-m-SciCThEyk2p5bSLmL75vpTLR`, `portfolio_runtime.py` ID `1Oy1Si3--NtCJPpo2FYqCckYrN0b2Fbqd`.
- Published recovered package-local implementations with relative imports: `app/runtime/ftmo_paper_guard.py` `ed63e92a`, `app/runtime/ftmo_pretrade_v2.py` `b17c2d56`, `app/runtime/portfolio_runtime.py` `ffe62b80`. V4 import wiring `a5923a06`, V5 wiring `5444de84`. These are adapted copies, not byte-identical Drive originals.
- Published `tests/test_ftmo_paper_integrated.py` `22e556bb`: PAPER pretrade -> open -> V5 bar -> V4 exit -> equity + day rollover; invalid OHLC must not advance day.
- **2/2 PASS** locally with recovered original dependencies and adapted package imports, `PYTHONPATH=/mnt/data/et_integrated python -m unittest discover -s /mnt/data/et_integrated/tests -v`. This is an isolated reconstructed test tree, not a clean GitHub checkout. Test code was copied from the published tests; source was reconstructed from recovered originals plus previously published V4 correction.
- No broker calls, real orders, production mutation or merge. Full regression/CI, original SHA lineage for adapted files, broader agents/steps integration and E2E remain open.


## FTMO V4/V5 malformed input regression — 2026-11-22
- Verified recovered original V4/V5 and PAPER dependencies from Drive; existing package-local GitHub sources read back before patch.
- V4 `process_bar` formerly leaked `KeyError` or `TypeError` for malformed input; hardened to return `ValueError` without mutating account, commit `6c809a67fe612a0ef47592c827003de597113e7d`.
- Existing integrated regression extended with four malformed inputs (null, empty, missing keys, nonnumeric OHLC), commit `061b805a9f5ac2596d5765064c757dcab3151eef`.
- Local reconstructed package regression: first run **2 PASS / 1 ERROR** because local V5 was stale (not matching published GitHub source); replaced local V5 with current published source, reran **3/3 PASS** in `/mnt/data/et_integrated` using `PYTHONPATH=. python -m unittest discover -s tests -v`. The test validates V5 fail-closed and account immutability, not clean GitHub checkout or E2E.
- No real orders, merge or production changes. Broader regressions and runtime certification remain open.


## FTMO ExecutionV6 — historical recovery and intrabar fix
- Recovered original `ftmo_execution_v6.py` Drive ID `170YBYAeaNHlrG8mmCCP_U5-J-6lSPfs2` and original V6 tests `1pCAHOOYDc79c1LyJvf1X8L03Ri8cQakN` from folder `1HKIhxsTAqjrPVL72Mg0wLLSpv1I_q2o8`.
- Found bug: original V6 derived `intrabar_breach` by scanning a sliding audit window, so an old breach could be reported as the current bar's event. Replaced with a per-call `breach` flag. Hardened malformed bar/day inputs and adapted imports to existing PAPER package.
- Published `app/runtime/ftmo_execution_v6.py` commit `27e4a3330cfa1167fc34679d31b7443f7ef3895e` and `tests/test_ftmo_execution_v6_intrabar.py` commit `ed3e3431215d9048c5c861ab0b40af87a24c8dcf`.
- Local isolated reconstruction `/mnt/data/et_integrated`: **31/31 PASS** original historical V4/V5/V6/Portfolio tests (8+8+5+10) and **3/3 PASS** existing integrated tests, via `PYTHONPATH=. python -m unittest discover -s original_tests -q` and `PYTHONPATH=. python -m unittest discover -s tests -q`. The three new V6 regression cases were published but were not yet executed against a clean GitHub checkout.
- V6 remains conservative OHLC worst-case proxy, not a tick-level reconstruction or FTMO E2E certification. PAPER only; main and production unchanged.

- Follow-up execution: new V6 regressions also executed locally with matching reconstructed source and tests: **6/6 PASS** (3 V6 + 3 integration), `PYTHONPATH=. python -m unittest discover -s tests -v`, 0.001s. Combined original 31 + integrated 6 = **37/37 PASS** across two offline invocations. This is not a clean GitHub checkout or E2E.


## FTMO Certification Gate V7 — recovered and fail-open bug fixed
- Drive folder `CERTIFICATION_GATE_V7` ID `1tnpQ9Q9JPoIfcDAJVPT9v-KXSu6YjBj4`, original source ID `1vyprf9epfAQ-w8oyfyPU0t04U3jV1qK7`, original tests ID `11QrsSuIkdbxDY5e-W23wHs94ratRw8yk`.
- Reproduced original critical bug: `assess(dict.fromkeys(REQUIRED,True), paper_tests_pass='FAIL')` returned `release_authorized=True` because of `bool('FAIL')`. Original **6/6 PASS** despite vulnerability.
- Corrected source rejects non-boolean `paper_tests_pass` and non-mapping evidence, preserving required keys and explicit boolean semantics; `app/runtime/certification_gate_v7.py` commit `3557bdb176b1a7261d23373cffa56c435db98459`.
- Published original 6 tests plus 3 adversarial cases `tests/test_certification_gate_v7.py` commit `0ed74ff36a7e409253fd7a9fe2e2ba77c06ddc73`. Local original-plus-patched **9/9 PASS** `python -m unittest -q test_certification_gate_v7` in `/mnt/data/et_v7_lab`; source is adapted for package path in GitHub, not clean-checkout CI.
- `release_authorized` is an evidence-gate boolean only; does not authorize real broker orders. Required evidence is not complete; E2E_CERTIFIED=FALSE. No main merge or production mutation.


## FTMO V8 historical consolidation recovery — 2026-11-22
- Newly located Drive folder `CONSOLIDATION_V8` ID `1qVZorwqL7O5r_tka_WMczlKKmxigRFJF`; original script `consolidate_v8.py` ID `1f3D5QtQSKFyYQMopRujfzjiT1Sydah6q`, consolidation ledger ID `1Yxvu-v_zTeUOEjw1UhbxS4-73-Chz5B9`.
- Original V8 was hard-coded to an old isolated `eldora_ftmo_v7` directory, with outputs written beside the script. Published adapted `tools/consolidate_ftmo_v8.py` commit `8bff81e019984c35bce3a2154101812c09d05041`: explicit source/out/package-root, rejects output inside source, rejects missing modules/tests and preserves `ftmo_release=BLOCKED`.
- Local isolated equivalent `/mnt/data/et_v8_lab/consolidate_v8.py` executed against reconstructed V4–V7 source/tests with package-root `/mnt/data/et_integrated`: **37/37 PASS**, 7 modules, 5 test files; same-tree output attempt rejected (exit 1). This was not a clean checkout of published V8.
- Original Drive V8 manifest labels its seven modules `isolated_paper_candidate_not_canonical`; no authority to claim runtime certification. No main merge, production change, paid resource or real orders.


## V8 evidence immutability fix — 2026-11-22
- Revisited original Drive V8 consolidation `1f3D5QtQSKFyYQMopRujfzjiT1Sydah6q` and its `READ_ONLY_CONSOLIDATION` mandate; original V8 ledger `1Yxvu-v_zTeUOEjw1UhbxS4-73-Chz5B9` explicitly marks seven motors noncanonical, FTMO release BLOCKED.
- Identified writable destination risk in the adapted V8: destination could be an ancestor of source or an existing evidence folder. Updated `tools/consolidate_ftmo_v8.py` to reject source/descendant/ancestor and nonempty destinations; commit `6f02c2a45e3a07529cbb65c98f32f643d1bbc487`.
- Published `tests/test_consolidate_ftmo_v8_safety.py` commit `cf83c1862b32e53dba8493aaa1246f569935ee39` (5 scenarios: source, descendant, ancestor, existing evidence, missing modules).
- **5/5 isolated safety scenarios PASS** with a locally reconstructed matching guard: four directory-safety checks plus missing-source fail-closed return code 2 and `ftmo_release=BLOCKED`. Published test file not yet executed in a clean GitHub checkout; no E2E certification.
- Drive discovery additionally queried agent and STEP registries; no new Trader-specific registry was confirmed from those queries. Do not claim agent activation or step integration.


## V6 empty-bar false intrabar breach — 2026-11-22
- Reopened original Drive V6 `170YBYAeaNHlrG8mmCCP_U5-J-6lSPfs2` and compared with isolated GitHub V6. Reproduced in local `/mnt/data/et_integrated`: previously halted PAPER account, balance/equity 90000, zero positions, `process_bar({})` incorrectly returned `intrabar_breach=True` and appended a new risk event.
- Fix: `breach = bool(validated) and account.balance+worst <= max(daily_floor,total_floor)` in `app/runtime/ftmo_execution_v6.py`, commit `e6e00aa02e0323b5e900ea1e0f3e0366f3cc445a`. Preserves historical `halted=True` while preventing fabricated new intrabar event.
- Regression published in `tests/test_ftmo_execution_v6_intrabar.py`, commit `d4ac9338e0d177fdfa125e878bfa9918e8d06c2d`. Local reconstructed matching sources/tests **7/7 PASS** via `PYTHONPATH=. python -m unittest discover -s tests -v` in `/mnt/data/et_integrated`.
- Test environment is isolated, not a clean GitHub checkout. Original Drive files unmodified. No real orders, production mutation, merge, or E2E certification.


## V6 datetime/day fail-closed regression — 2026-11-22
- Reproduced locally using reconstructed package `/mnt/data/et_integrated`: `ExecutionV6.process_bar({}, day=datetime(2026,10,30))` raised Python `TypeError` during comparison against `date(2026,10,29)`; `isinstance(datetime,date)` was too permissive.
- Changed V6 day gate to `type(day) is date`, rejecting datetime before any account mutation. Source commit `2e67839a7871707eb52571ece738c00d43d3a0c3`.
- Added `test_datetime_day_rejected_before_mutation` to V6 regressions, test commit `9725b9a9d232b320655b3cea1ac6bcba39d8b81a`.
- Ran `PYTHONPATH=. python -m unittest discover -s tests -v` in `/mnt/data/et_integrated`: **8/8 PASS**, 0 failures. This is reconstructed isolated code, not a clean GitHub checkout.
- Drive search for FTMO_PAPER, DUAL_MODE_ENGINE, EXECUTION_V9 and RISK_ENGINE found noisy historic evidence but no newly certified Trader agent/STEP. Original Drive files untouched, no real orders, no merge, E2E false.


## FTMO V6 -> V7 PAPER wiring and MIND agent registry — 2026-11-22
- Git clone attempt `git ls-remote https://github.com/engrobertooliveirafilho-beep/mind-fin-pro-backend-core.git` failed because local execution container cannot resolve `github.com`. Do not claim clean-checkout certification.
- Added four actual V6→V7 wiring tests in `tests/test_ftmo_v6_v7_wiring.py`, commit `dae976f60bac3cbf51e610758de01f05b6840574`. In reconstructed isolated `/mnt/data/et_integrated`, first run **11/12 PASS, 1 FAIL** because local V7 was stale (truthy `paper_tests_pass='PASS'` accepted). Replaced local V7 with exact content of isolated GitHub branch and reran `PYTHONPATH=. python -m unittest discover -s tests -v`: **12/12 PASS** (8 existing + 4 wiring). Tests cover PAPER success not unlocking evidence, V6 risk halt not overridden, malformed bar not advancing day/gate, and rejecting untyped V7 test result.
- Reopened MIND original agent registry from Drive ID `1IGBrD8FL3CLfVMngnG0rA765KlaZKfoD` (81 agents). Found `domain.economics_finance_markets`: 13 STEP references `124,136,139,154,170,177,190,210,211,239,281,497,498`, `agent_health.status=unknown`, `human_approval_required=true`, `can_change_code=false`, `can_only_emit_blueprints=true`. Found `auto_evo.risk_alignment_guard` without proven STEP mapping or health. Registry labels `active/auto_run` are configuration claims, not runtime execution evidence.
- **Agent/STEP status: discovered/reconciled as documentary candidates only; not activated, not wired to FTMO, no executable certification.** PAPER_ONLY, real orders forbidden, main and Drive originals untouched.
