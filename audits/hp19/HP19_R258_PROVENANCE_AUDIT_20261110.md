# R258 — Provenance consistency audit

Offline test command: `cd /mnt/data/HP19_R258 && python -m unittest -v test_provenance`.

8/8 PASS (0.037s): duplicate agent, duplicate log, incomplete entries, forged/self-reported runner identity, symlink, log tamper, unknown runner, mismatched run ID.

**Important**: this validates only manifest consistency, file integrity, and a supplied runner allowlist; it does not authenticate the runner. An attacker controlling manifest and files could forge matching digests. The final result is unconditionally `AUTHENTICITY_UNVERIFIED` and no certification is possible. No source integration into production. HP19 0/19.
