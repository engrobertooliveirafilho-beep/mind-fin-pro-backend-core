# STEP457 — Offline canonical wrapper regression

2026-11-21. Original compute motor restored from Google Drive ID `1DwexrLN9XU1vyYml04jocMo9-Y2GtJ2h`; historical broken wrapper from Drive ID `13go66hPaCVmujM2Ou4abf6KLlERd2wC2`. Original motor preserved; corrected canonical wrapper in isolated branch.

**Execution:** `python -m unittest discover -s tests -v` from isolated `/mnt/data/step457_run` => **10 tests PASS**, 0 failures, ~0.001 s. Offline. Log SHA-256 `a0a10f26ec9a88aba722807424d49828acdac4f2ee1f7231960556e21dbf6978`.

**Verified identical Git blob hashes for locally executed files:**
- `app/step457_gpu_autoscaling/engine.py`: `b15d14ed26be69e32b88d8f0dc2285dfe5bbaa27`
- `tests/test_step457_canonical_recovery.py`: `330a97a960c130c7a0d29225113e5cc57774e0fd`

The locally transcribed original `app/infra_gpu_autoscaling.py` differs in line endings from the published Drive original; **byte-identical execution of that file is not certified**. Tests confirm functional behavior of the locally reproduced algorithm plus exact published wrapper/tests.

**Findings:** Original algorithm silently normalizes NaN and infinity and silently increases zero/inverted capacity limits. Wrapper now rejects invalid nonfinite inputs, inverted limits, zero maximum capacity, unknown parameters and non-integral/negative counts. It only returns an offline capacity proposal, never provisions GPUs.

`PAPER_ONLY=TRUE | GPU_REAL=OFF | E2E_CERTIFIED=FALSE | MAIN=INTACTA | COST=R$0`
