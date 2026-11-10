# R264 — Ledger reset fix, offline verified

Local command: `cd /mnt/data/HP19_R264 && python -m unittest -v test_replay_gate`.
Result: **37/37 PASS**, 0.393 seconds (includes inherited tests). The revised isolated gate requires a pre-provisioned SQLite ledger opened with `mode=rw`, rejects missing/deleted/renamed ledger, symlinks, invalid schema, and duplicate run IDs. It never recreates a missing ledger.

**Residual:** a replacement SQLite database with valid schema but missing replay history remains an unresolved rollback attack. Require independently anchored append-only audit state and trusted runner before any activation. No main/production changes. HP19 0/19.
