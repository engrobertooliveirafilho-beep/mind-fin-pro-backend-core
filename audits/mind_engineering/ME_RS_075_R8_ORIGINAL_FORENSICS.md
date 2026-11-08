# ME-RS-075 — R8 original ZIP forensic inspection (2026-11-08)

Source: user-uploaded `ME_RS_067_EVIDENCE_20261108T003637Z.zip`.
Archive SHA-256: `b15db9f692e73a20558921a578e5764b324fe53e3e464b6db87a2ef45e39c3b5`.
Archive members: 52 (R7 original, 50 R8 candidates, manifest).
R7 original byte SHA-256: `58e559debb6181b4a34f857572a3fd1c84f1994def82637ad696106aaecd9d63` — matches manifest.

## R8 candidate offline tests (executed in isolated Linux temporary directories)

| Executor | Offline resume regression 044 | Version history regression 045 |
| --- | --- | --- |
| `004_local_bridge_v2.py` | PASS | PASS |
| `008_local_bridge_v2_integrity_candidate.py` | FAIL | PASS |

**Interpretation:** regression 044 asserts a same-size, same-mtime content change is *not detected* and marks `same_size_same_mtime_change_detected: false`. The integrity candidate 008 deliberately re-hashes before reusing metadata, so it correctly detects such a content change and fails the **legacy test expectation**. This is a test-contract conflict, not proof that the integrity candidate is unsafe. Do not weaken integrity checking to satisfy regression 044. Author a new test expecting detection and inspect journal semantics before promoting candidate 008.

Both executors pass the three-version append-only journal regression. All tests used temporary synthetic fixtures and did not access Drive, production databases or Git remotes.

## Further gates

- Verify every archive member SHA-256 against MANIFEST.json.
- Inspect R8 authority and original checkpoint 11/32 provenance; ZIP is a set of candidates, not proof of the historical running executable.
- Test candidate 008 with a corrected same-size/same-mtime regression, crash/restart and malformed journal.
- Keep PR draft and production unchanged. No R8 certification.
