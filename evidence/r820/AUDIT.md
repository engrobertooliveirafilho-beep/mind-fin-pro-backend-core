# R820 — Byte-identical GitHub regression certification
Date: 2026-11-22

## Prior state
R819 observed mismatched local Git blob hashes for R818 original source and test. R820 fixes evidence provenance, not application code. R809–R819 work preserved without repeating historical recovery.

## Provenance verified
GitHub R818 original source `app/runtime/capability_recovery_bridge.py` blob SHA-1: `966d5d2c2b9827d96cb03d33526c30a39726cabb`.
GitHub R818 regression `tests/test_r817_capability_helpers.py` blob SHA-1: `a7bb7dddc5f51a3eee7de16d54ffe43cdfc72559`.

Reconstructed exact UTF-8 bytes in a local repository-shaped tree; recalculated Git blob SHA-1 for each file and confirmed exact equality with both published GitHub blob IDs. Original source SHA-256 `bbe929c6a5a1edbe79b2f4a1cfa38ce7504a6684113df676c8d0c0fb9666edf2`. Original tests SHA-256 `2552800f36011ecdbda7c61183ac01ef98a420cc998d5eeeb06fafefd8c013f1`.

## Actual execution
Command: `python -B -m unittest discover -s tests -p test_r817_capability_helpers.py -v`.
Executed with the byte-identical GitHub files in `app/runtime/` and `tests/` local layout. **12/12 PASS, 0 failures, 0 errors**. See `tests.log`.

## Limits
This certifies only the R817 helper/report regression under a local isolated Python runtime. It does not certify application startup, deployed production, any live agent capability, HP19 functional execution, or full E2E. Main unchanged. Cost R$0.
