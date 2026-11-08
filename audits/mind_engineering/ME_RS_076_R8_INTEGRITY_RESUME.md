# ME-RS-076 — R8 archive integrity and corrected offline resume

Source: user-uploaded `ME_RS_067_EVIDENCE_20261108T003637Z.zip`, archive SHA-256 `b15db9f692e73a20558921a578e5764b324fe53e3e464b6db87a2ef45e39c3b5`.

## Archive verification

Read `MANIFEST.json` directly and verified **all 50** `files[]` entries against archive member byte length and SHA-256. Result: **50/50 PASS, 0 mismatches**. The archive contains 52 members total (50 candidates, original R7 executor, manifest).

## Corrected R8 integrity regression

Executor: `R8_CANDIDATES/008_local_bridge_v2_integrity_candidate.py`, extracted as-is from the archive.

Regression: `R8_CANDIDATES/044_R8_OFFLINE_RESUME_REGRESSION.py`, executed from a disposable copy with only the following assertion/expectation changes:
- After same-size/same-mtime mutation: expect `reused == 0` and `hashed == 1` instead of the inverse.
- Journal length: expect `3` instead of `2`.
- Report `same_size_same_mtime_change_detected: true`.

Executed in an isolated local Python process with temporary synthetic fixtures: **exit 0**, first hash PASS, unchanged reuse PASS, same-size/same-mtime change detected true, changed-size rehash PASS, journal records 3. No Drive, production executor or Git remote was accessed by the test.

## Boundaries

- This test corrects a legacy contract that implicitly accepted undetected file content mutation; do not weaken the candidate's SHA-256 recheck.
- Original R8 checkpoint 11/32, interrupted journal recovery, malicious/partial journal lines, and R6→R7→R8 historical integration remain unverified.
- R8 is NOT globally certified; PR remains draft; no production changes.
