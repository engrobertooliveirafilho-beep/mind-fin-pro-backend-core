# R260 — Combined signed provenance and file integrity (2026-11-10)

Local execution: `cd /mnt/data/HP19_R260 && python -m unittest -v test_combined_gate` → **8/8 PASS** in 0.036 s.

Checks: Ed25519 signature, bound runner identity, 19 file digests, duplicate agents, missing logs, tampering, unknown signer, signed runner mismatch. Test fixture creates synthetic sources/logs; results **do not certify behavior or authentic institutional runner**. Even valid signatures and digests return `certified=False` pending independent behavioral review. HP19=0/19. No main/production changes.
