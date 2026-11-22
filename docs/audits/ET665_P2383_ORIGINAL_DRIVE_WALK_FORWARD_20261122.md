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


## V5 strict date validation and Drive FTMO profile discovery — 2026-11-22
- Reproduced original V5 `ExecutionV5.process_bar({}, day=datetime(2026,10,30))` leaking `TypeError` on date comparison; fixed by requiring exact `date` type before any day rollover. Source `app/runtime/ftmo_execution_v5.py` commit `310b5ff0151ee7554cdd6a9d8910ff30c461f7be`; regression `tests/test_ftmo_execution_v5_day_contract.py` commit `00bca5a5b9b0ee2dc84478dd0b7d733aacbba84d`.
- Local reconstructed package `/mnt/data/et_integrated`: `PYTHONPATH=. python -m unittest discover -s tests -q` **15/15 PASS** (existing 12 + 3 V5 day-contract tests); no clean GitHub checkout or E2E.
- Deep Drive folder `FTMO_CERTIFICATION` ID `1o1scbwKgSwZx0pFHbP97rVVLCeSvTACn` revealed additional child `FTMO_PROFILE_V3_20261121` ID `1kkmtUckX3QI0l9AoKIltaiusPV9j2ubt`; folder listing currently empty, **no verified profile implementation or rule update**. The FTMO rules-current gate remains false.
- Reused historical V2–V8 engines and controls rather than creating duplicate runtime. Original Drive files read-only, isolated branch only; no real orders, merge or production changes.


## V8 timeout evidence preservation and 46/46 reconstructed regressions — 2026-11-22
- Reexecuted existing historical and integrated tests in reconstructed `/mnt/data/et_integrated`: `PYTHONPATH=. python -m unittest discover -s original_tests -q` **31/31 PASS**, and `PYTHONPATH=. python -m unittest discover -s tests -q` **15/15 PASS**, total **46/46**. This is not clean checkout or E2E.
- Discovered V8 `subprocess.run(...,timeout=90)` raised `TimeoutExpired` before writing audit and SHA manifest. Fixed `tools/consolidate_ftmo_v8.py` to record timeout as blocked returncode 124 and persist `REGRESSION_V8.txt`, `CONSOLIDATION_V8.json`, `SHA256_V8.json`; commit `e03658119721847fa74314f3d5fd44d2533c21e9`.
- Ran one isolated timeout-injection regression against matching reconstructed V8 code with `unittest.mock.patch(subprocess.run)`: **PASS**, returncode 124, all 3 evidence files persisted, `ftmo_release=BLOCKED`, `real_orders=0`. Added published regression to `tests/test_consolidate_ftmo_v8_safety.py`, commit `4e665df0f216876fbfaa0562853add468ef92fab`. Published version not run from a clean GitHub checkout.
- Drive search for `FTMO_PROFILE_V3`, `TRADER_CAPABILITIES`, `TRADER_MOTORS` found only previously known empty profile folder and older dossiês; no new executable motor, STEP or agent certified.
- Original Drive immutable, main and production untouched; PAPER only, FTMO release blocked.


## Portfolio direct rollover atomicity — 2026-11-22
- Confirmed original Drive `portfolio_runtime.py` ID `1Oy1Si3--NtCJPpo2FYqCckYrN0b2Fbqd` and GitHub isolated runtime. Direct `PaperPortfolio.new_day` previously called `_mark_all()` before validating the day; rejected old or datetime dates could mutate equity/risk halt.
- Corrected existing `app/runtime/portfolio_runtime.py` to reject `type(day) is not date` and `day <= account.day` before marking. Commit `be0491cc29f27885ffc8dd91bf34bc2d0956e9a8`.
- Added three tests in `tests/test_ftmo_portfolio_direct_rollover.py` commit `e80904145ed933981132c2b17373526d1f1e9306`: datetime rejection without equity/audit mutation, earlier date rejection without mutation, valid rollover re-marks open position.
- Executed in reconstructed local `/mnt/data/et_integrated`: `PYTHONPATH=. python -m unittest discover -s original_tests -q` **31/31 PASS** and `PYTHONPATH=. python -m unittest discover -s tests -q` **18/18 PASS**, total **49/49 PASS**. Not a clean checkout or E2E certification. PAPER_ONLY; main/production/Drive unchanged.


## Direct V2 account date safety and authoritative V2 audit — 2026-11-22
- Recovered original Drive PAPER guard V2 folder `1YJKPzft3z-niELyNP78wkVbFmV-cekOq` and `V2_AUDIT.json` ID `15QBj75OOMIL7xNqXINrMA5OBTQQBa5oe`: historical **21 tests PASS, 0 FAIL**, but explicitly `integration_with_canonical_runtime=NOT_EXECUTED`, `ftmo_readiness=NOT_CERTIFIED`, missing account timezone-specific day reset, independent market campaign, broker integration, automatic open-position marking, worst-case slippage and official FTMO rule equivalence. These are documentary limits, not newly verified behavior.
- Corrected `app/runtime/ftmo_paper_guard.py` `PaperAccount.new_day` to reject `datetime` before any day mutation; commit `0797f5a70e9253469ec76725dd565fb102058167`. Added three direct-account date tests `tests/test_ftmo_account_day_contract.py` commit `47df0e13b3ae8f799689795ad2ac5fed808e9e82`.
- Executed locally in reconstructed `/mnt/data/et_integrated`: **31/31 historical + 21/21 integration = 52/52 PASS**, no clean checkout, no E2E.
- FTMO timezone-specific day reset remains a known explicit V2 limitation; no claim of official FTMO compliance or real-order readiness. PAPER_ONLY, Drive originals immutable, main and production untouched.


## V2 PAPER timezone-local rollover — 2026-11-22
- Drive V2 audit ID `15QBj75OOMIL7xNqXINrMA5OBTQQBa5oe` explicitly documents missing account timezone-specific day reset. Implemented optional `PaperAccount.rollover_at(instant,account_timezone)` in existing `app/runtime/ftmo_paper_guard.py`, commit `8440c79e859c4f7a1a48700a153e49ee4fcc2ce8`.
- Caller must supply timezone-aware datetime and explicit valid IANA timezone. Convert instant to local calendar day; no-op on same day, reject backward day, call existing validated `new_day` on forward day. No implicit broker or FTMO timezone assumption.
- Added four boundary/invalid-input tests `tests/test_ftmo_timezone_rollover.py`, commit `8104a44c2cba9c9b8a88ea16a1aeb7f5261f6113`. Executed in reconstructed local `/mnt/data/et_integrated`: **31/31 historical and 25/25 integrated PASS**, **56/56 total**. No clean GitHub checkout or E2E certification.
- Not integrated into a canonical timestamp ingestion or broker feed; official FTMO rule equivalence, actual account timezone and daylight-saving-specific cases remain unverified. Main, production and Drive originals untouched; PAPER_ONLY.


## V2 account creation chronology and MT5 profile provenance — 2026-11-22
- Reproduced locally: `PaperAccount.create(rules, datetime(2026,10,29))` accepted a datetime as the initial calendar day. Corrected `app/runtime/ftmo_paper_guard.py` with exact date validation, commit `dcd4871269fe7f4783854b6b7362aa43691a65cc`.
- Two regression cases (datetime and string rejected at creation) added to `tests/test_ftmo_account_day_contract.py`, commit `d63fe1b1e1342f3adcbbf17bfa4a2b037c6dbb92`. Executed local reconstructed package: **31/31 historical + 27/27 integrated = 58/58 PASS**, no clean checkout.
- New Drive provenance: `MT5_FTMO_PROFILE` folder `15VVqyAPHtgSHGK260gf0yeiadHKabY3Y` contains profile hash folder `1EpyyNkS7codhYoF9J5KWFiE2UKx9z88Z`, with `MQL5`, `llm-agent`, `bases`, `config`, `logs`, `temp`, `origin.txt`. Agent subfolder `162sQ0H4XdNOIv6M1Wch1NsyQuxV9PVRc` contains `state` and `data`. These are new **historical inventory leads**, not verified runnable Trader agent/motor/STEP or authorized MT5 integration. Do not fetch or publish credentials/config secrets. No live MT5 access.
- FTMO timezone rule equivalence and E2E remain blocked; main, production, original Drive immutable.


## V2 numeric atomicity and newly recovered MT5 SIMBROKER source — 2026-11-22
- Reproduced critical V2 PAPER guard defect: `close_paper_trade('BUY',100,'NaN',1,1)` raised `decimal.InvalidOperation` **after** contaminating balance/equity with NaN; `status()` then also failed. Corrected existing guard to prevalidate all six numeric inputs as finite, require positive prices/quantity/point value and nonnegative costs, and reject nonfinite PnL before mutation. GitHub source commit `9d64fed04da709fdd3115112bae21c3bc96cd379`.
- Added three regressions `tests/test_ftmo_paper_numeric_atomicity.py` commit `3227e474afee3d5b9642b7c64bc2b4dfc0e8f75c`. Executed reconstructed local tests: **31/31 historical + 30/30 integration = 61/61 PASS**. Clean GitHub checkout/E2E not certified.
- **New Drive source found:** `MT5_FTMO_PROFILE` > `MQL5/Experts/MIND` folder `1AfaQzG0nnhgiPz4FroqsCl5pCWYzCDJs` contains MQL5 `MIND_FileBridge_P2829_SIMBROKER.mq5` ID `1Jbn0_h6-t0CicmllwdDHY04ZCJ32uAj5` (4480 bytes), `MIND_Replay_HUD_P2833.mq5`, `MIND_Replay_HUD_Controls_P2834.mq5` and prior FileBridge variants. Source inspected read-only. P2829 explicitly logs `MODE=SIM_BROKER`, `REAL_ORDERS=FORBIDDEN` and writes simulated ledger; no `OrderSend` in source.
- **New P2829 defect:** when requested symbol has no valid quote, source falls back to chart `_Symbol` price, risking false-symbol simulated fill. Also `last_raw` is advanced before validation, suppressing retries of malformed or temporarily unpriced signals. Local isolated candidate `/mnt/data/MIND_FileBridge_P2829_SIMBROKER_SAFE.mq5` removes cross-symbol price fallback, rejects unavailable quote, defers `last_raw`; static assertions PASS, **not compiled, not published, not functionally certified**. Original MQL5 remains untouched; live MT5 forbidden.
- PAPER_ONLY, real orders forbidden, main/production untouched.


## P2829 SIMBROKER isolated recovered candidate — 2026-11-22
- Original MQL5 Drive file `MIND_FileBridge_P2829_SIMBROKER.mq5`, ID `1Jbn0_h6-t0CicmllwdDHY04ZCJ32uAj5`, inspected read-only. Created **adapted** PAPER-only isolated candidate `recovered/mt5/MIND_FileBridge_P2829_SIMBROKER_SAFE.mq5` commit `f5fc123e4aa029962359a2e78c93d1e4af08fbfe`, no modification of original, no deployment.
- Rejects symbol-selection and quote failures without using chart-symbol prices; validates lot finiteness; acknowledges `last_raw` only when simulated ledger write succeeds, preserving retries after ledger failure. No trading API in published source.
- Published static regression source `tests/test_p2829_simbroker_static.py` commit `eb7b7c42c55055676ecf2df6bead61fe385c6a89`. GitHub connector readback and **5/5 source assertions PASS** against published MQL5; **no MetaEditor compile, no MQL5 runtime test, no broker integration, no E2E certification**. Historical 61/61 Python PASS from earlier reconstructed package not rerun in this operation.
- Note: the isolated candidate is an adaptation, not byte-identical Drive original; its parser and ledger behavior must be compared with original and exercised in an offline MQL5 environment before promotion. FTMO real orders forbidden.


## P2829 additional fail-closed repairs and Trader1 Drive inventory — 2026-11-22
- Isolated MQL5 SIMBROKER candidate now aborts `OnInit` when simulated ledger header creation fails; CSV-escapes raw signal/tag/symbol; rejects malformed lot characters and lots that round to zero at ledger precision. Existing `recovered/mt5/MIND_FileBridge_P2829_SIMBROKER_SAFE.mq5` updated commit `4a2aa85c247c8f23fab9ae25649d404999647cde`.
- Added 3 static assertions in existing `tests/test_p2829_simbroker_static.py` commit `1fb8ab87105cdae7195dcb6c9d1679b18fd07827`. Readback source inspected; 9/9 inline source checks PASS. This is **not** MQL5 compile or runtime execution. Historical Python 61/61 tests not rerun in this operation.
- Drive `MT5_FTMO_PROFILE/MQL5/Experts/Trader1` ID `1PpIA8Spe0zlJcxZEqyZzIttsOHxtv_T9` contains original `TRADER_1_007_R5_R2_CANONICAL_EXPORTER.mq5` ID `1ZZBtTn2r4jj4CHnTgGcnBfkT-rslJ2zL` and EX5 binary. `Experts/Advisors` ID `1asXPWTQGnVTv1yUez4Fo58bZ34K1J_W5` contains four example EA sources: `ExpertMAPSARSizeOptimized.mq5`, `ExpertMAPSAR.mq5`, `ExpertMAMA.mq5`, `ExpertMACD.mq5`. **Inventory only**, no evidence of canonical integration, certified agents or live execution.
- No real orders, no MT5 deployment, main/production and original Drive unchanged. PAPER_ONLY, E2E_CERTIFIED=FALSE.


## Trader1 original exporter preflight — 2026-11-22
- Fetched and decoded original UTF-16 LE MQL5 Drive source `TRADER_1_007_R5_R2_CANONICAL_EXPORTER.mq5`, ID `1ZZBtTn2r4jj4CHnTgGcnBfkT-rslJ2zL`, 784 lines. Original default config: `InpWindowDays=31`, `InpMinimumBars=500`, `InpMaximumBars=0`. OnTimer waits for connected FTMO-labelled server and then exports history using `CopyRates`; no MQL5 trading call found during targeted inspection.
- Original export loop uses `window_end=cursor+(InpWindowDays*86400)` and `cursor=window_end+1`. Nonpositive window size may cause invalid cursor progression; `InpMaximumBars` below minimum makes success impossible. Added separate fail-closed PAPER-only Python preflight `app/runtime/trader1_exporter_config_gate.py` commit `85c4e85eea740494a01a7606712ecf270952978e`, without changing Drive MQL5.
- Added 8 tests `tests/test_trader1_exporter_config_gate.py` commit `b721662c72256104c72f5e06cf92250150993e18`; executed 8/8 PASS offline in reconstructed local package. This is **not** compiled or integrated with MQL5 exporter; original still needs in-source preflight and offline compilation before any activation.
- No credentials retrieved, no MT5 connection, no real orders; main, production and Drive originals unchanged. E2E_CERTIFIED=FALSE.


## Trader1 original source patcher and 74 offline regressions — 2026-11-22
- Reopened original Drive `TRADER_1_007_R5_R2_CANONICAL_EXPORTER.mq5` ID `1ZZBtTn2r4jj4CHnTgGcnBfkT-rslJ2zL` (UTF-16 LE, 784 lines). Confirmed exact `OnInit` indentation and `InpWindowDays=31`, `InpMinimumBars=500`, `InpMaximumBars=0`; source exports historical rates after FTMO-labelled connection. No trade API found in targeted source scan.
- First local source patch attempt failed 3 tests due to indentation mismatch; fixed exact-match anchor and reran successfully. Published `app/runtime/trader1_exporter_source_guard.py` commit `5364bcf24ebe67f4574a50671ab51c477d5334b6`: applies fail-closed configuration validation before file/timer initialization and rejects unexpected source or second patch.
- Published five portable source-guard regressions `tests/test_trader1_exporter_source_guard.py` commit `ba9a496f6be60fd366cfdf5df7b5bee723316d2f`. Locally verified patch on exact original Drive text; executed reconstructed Python suites **43/43 integration + 31/31 historical = 74/74 PASS**. Tests run offline in reconstructed workspace, not clean GitHub checkout.
- Source patcher published; patched full MQL5 exporter **not** published or compiled. Source-level patch cannot certify MT5 execution, agent activation, or E2E. Original Drive, main and production unchanged; PAPER_ONLY, REAL_ORDERS=FORBIDDEN.


## Trader1 source digest gate and MIND agents provenance — 2026-11-22
- Reopened original Drive `TRADER_1_007_R5_R2_CANONICAL_EXPORTER.mq5` ID `1ZZBtTn2r4jj4CHnTgGcnBfkT-rslJ2zL` as UTF-16 LE, 16,049 Python characters. SHA-256 of normalized UTF-8 text: `0c3f8cc58a13aaa0f7acc1fdfaae6ada89304c68cd3616f677679a211a6fa19e`. This hash is for decoded UTF-8 text, **not** original Drive binary.
- Hardened existing patcher `app/runtime/trader1_exporter_source_guard.py` to require independent SHA-256 before source mutation and reject trading API tokens, commit `1ccfcf05dd681e4a13197d96b57bc207230c78a0`. Extended `tests/test_trader1_exporter_source_guard.py` with hash mismatch, injected trading API and absent digest cases, commit `bae8f913472cf79705360b96521ecc67a888be4b`.
- Generated local isolated full patched MQL5 `TRADER_1_007_R5_R2_CANONICAL_EXPORTER_PAPER_HARDENED.mq5` with strict OnInit input validation; six local source assertions PASS. **Full patched MQL5 not published to GitHub or compiled**, and no MT5 runtime tests. Original Drive source preserved.
- Reopened MIND agents registry Drive ID `1IGBrD8FL3CLfVMngnG0rA765KlaZKfoD`: 81 registered agents. Finance strategist `domain.economics_finance_markets` has STEP references `124,136,139,154,170,177,190,210,211,239,281,497,498`; `auto_evo.risk_alignment_guard` is a registry entry. Registry `active=true` is metadata, **not** proof of runtime or trading authority. No agent activated.
- PAPER_ONLY, REAL_ORDERS=FORBIDDEN, main and production untouched, E2E_CERTIFIED=FALSE.


## MIND finance agent evidence gate — 2026-11-22
- Reopened original Drive agent registry ID `1IGBrD8FL3CLfVMngnG0rA765KlaZKfoD` and parsed 81 agents. `domain.economics_finance_markets` has 13 STEP references `[124,136,139,154,170,177,190,210,211,239,281,497,498]`, registry `active=true`, `auto_run=true`, but `agent_health.status=unknown`. `auto_evo.risk_alignment_guard` is present as a separate registry entry, without proven live integration. No STEP implementation certified.
- Implemented PAPER-only fail-closed `app/runtime/trader_agent_evidence_gate.py` commit `94d5c210fcb087aba16998d5a4898a5e5eebeaba`: registry metadata alone never certifies an agent. Requires positive runtime health, implemented STEPs, offline tests, PAPER integration and human approval. Rejects strings used as boolean flags.
- Added `tests/test_trader_agent_evidence_gate.py` commit `4e939420b030e8d9ee16692f4583403d5d310eb9`; executed 8/8 PASS in isolated Python offline environment. **Not integrated into live agent loader**; this is a standalone certification guard, not proof of agent runtime or E2E.
- No original Drive changes, no real orders, no main/production mutation. PAPER_ONLY; E2E_CERTIFIED=FALSE; COST=R$0.


## Finance STEPs 124/136/170 recovered as nonfunctional stubs — 2026-11-22
- Read actual original Drive text `step124_approved_stub.py` ID `1F9MfIvzFhb4awCEWjcsawTEgtlmLjT5m`, `step136_approved_stub.py` ID `130Y9fZW_3mxb7i-hbHzDdcK0fKjYBDne`, and `step170_approved_stub.py` ID `1ARqGyiPOXpzGqtYjnnzy8u3iKRd3dZAH`. Each declares `STEP_STATUS="approved_stub"` and explicitly states real logic must be implemented later. Administrative approval is not functionality.
- Reconciled with finance agent registry ID `1IGBrD8FL3CLfVMngnG0rA765KlaZKfoD`: these three are among its 13 referenced STEPs; finance agent cannot be certified on registry metadata.
- Published standalone AST-based STEP evidence inspector `app/runtime/step_source_evidence_gate.py` commit `e2446f64285f07ce2d01124234a3ef744e5d7255`. Explicitly rejects mismatched STEP IDs and malformed sources; marks approved stubs NOT_IMPLEMENTED; even `implemented` declarations are not automatically certified.
- Nine isolated Python tests **9/9 PASS** executed locally before publication; published `tests/test_step_source_evidence_gate.py` commit `1d6ff7023059500a809704fc300614fcb9c55c59`. No complete clean checkout, no agent loader integration, no E2E.
- Original Drive read-only, main and production intact, PAPER_ONLY, REAL_ORDERS=FORBIDDEN, COST=R$0.
