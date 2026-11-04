# P2279E — SHA-256 local verification and integration gate (2026-11-04)

Scope: **PAPER_ONLY**, no live orders, no production integration.

The 10 MT5 CSVs recovered from the authenticated Drive release boundary were downloaded as original raw files into the isolated analysis environment. A separate local Python `hashlib.sha256(path.read_bytes())` pass compared all 10 against the earlier connector-text SHA-256 values documented in `P2279E_MT5_REPLAY_EVIDENCE_20261104.md`.

**Result: 10/10 PASS (byte hashes match).**

This verifies that the locally recovered raw bytes agree with the authenticated connector-returned text used in the replay. It does not verify the datasets' market-provider provenance or independence from the strategy selection period.

Historical Python replay evidence is in `P2279E_ORIGINAL_PYTHON_REPLAY_20261104.md`: 12 processed, 11 approved, 1 weak; original algorithm run with only isolated path substitutions.

## Duplicate check
- Verified repository path `mind_trader/__init__.py` exists on the audit branch.
- GitHub indexed searches for `mind_trader`, `walkforward`, `robustness` and `EMA_CROSS` returned no matches. These searches are **not an exhaustive repository tree audit** and do not establish absence of functionally equivalent engines.
- No engine copied into production or registered as a new service.

## Remaining gates
1. Enumerate full repository tree and map existing strategy/backtest/robustness interfaces.
2. Compare recovered P2279E engine semantics and dependency contracts to existing modules; reject duplicates.
3. Build a portable replay harness and deterministic tests, with no broker adapters.
4. Test integration in an isolated PAPER_ONLY context.
5. Record test logs and commit SHAs; authorize merge only after explicit gates.

No original historical output CSV has been located for row-by-row provenance comparison. No FTMO or independent out-of-sample certification is claimed.
