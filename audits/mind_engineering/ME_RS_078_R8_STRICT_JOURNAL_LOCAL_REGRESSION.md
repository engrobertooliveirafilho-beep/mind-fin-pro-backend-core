# ME-RS-078 — R8 strict-journal candidate verification

Status: **5/5 PASS locally**, source not yet committed to GitHub.

Input: `ME_RS_077_R8_STRICT_JOURNAL_CANDIDATE.py`, supplied as an attachment in the preceding conversation, 9,481 bytes.

Executed five isolated Python unittest scenarios with temporary source and journal directories:

1. Baseline scan + idempotent replay: PASS.
2. Invalid JSON inserted in middle of journal: rejected with `JOURNAL_INTEGRITY_ERROR`: PASS.
3. Unterminated trailing journal record: rejected with `JOURNAL_UNTERMINATED_RECORD`: PASS.
4. Invalid 64-character SHA-256: rejected with `JOURNAL_INTEGRITY_ERROR`: PASS.
5. Same-size/same-mtime content mutation: rehashed while unchanged file reused: PASS.

Observed: `Ran 5 tests in 0.028s — OK`. Test harness saved locally as `test_me_rs_078_r8_strict_journal.py` and not yet published to GitHub.

**Not certified:** source candidate and test harness must be committed together to a dedicated audit branch and rerun against exact GitHub blobs. The historical 11/32 checkpoint, partial-journal recovery and integrated R4→R8 replay are not proven. Do not merge, promote or change production.
