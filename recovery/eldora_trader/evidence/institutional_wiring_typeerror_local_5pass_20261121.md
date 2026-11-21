# Institutional wiring TypeError retry guard — 2026-11-21

Published source: `app/runtime/mind_trader_institutional_wiring.py` Git blob `beba1d72c1892ab4f90b3c7b018fdedbc8b7e5c2`; commit `e53aec21c680a4a857f429205920c0e125b0f533`.
Published test: `tests/test_institutional_wiring_safety.py` Git blob `dd7347bdcf9ce981f58baee6759fa8f6244ea44b`; commit `cf46d1a515a07f7fedecac87b290de1a36a80830`.

Offline **local behavioral reconstruction** (not exact Git blobs) executed 5 isolated unittest cases: **5 PASS / 0 FAIL**. Local log SHA256 `bafdbcc36692990373926826f8e42d50dc23b55ad12afd844d4ba71a19798b43`. Verified that a `run(payload)` raising TypeError is called only once; other four cover import failure and health no-execution.

**Certification boundary:** current GitHub test suite and full app E2E **not executed** in this run; do not claim exact-source PASS. Existing historical 4/4 exact-source evidence refers to previous Git blobs only. PAPER only, main untouched.

## Canonical exact-source revalidation — 2026-11-21

Reconstructed the current GitHub engine and test bytes and confirmed `git hash-object` equality: engine `beba1d72c1892ab4f90b3c7b018fdedbc8b7e5c2`; tests `dd7347bdcf9ce981f58baee6759fa8f6244ea44b`. Ran `PYTHONPATH=. python -m unittest discover -s tests -p test_institutional_wiring_safety.py -v` in offline Python 3 environment: **5/5 PASS, 0 FAIL**, 0.002s. Log SHA-256 `0dce83c0a5981e80d96a236a2bf941883227bcbdbb2df257bc180d67b9136230`. This supersedes the earlier non-exact-source caveat **for these two Git blobs only**. Tests mock imported dependencies; no full runtime or broker E2E certification.
