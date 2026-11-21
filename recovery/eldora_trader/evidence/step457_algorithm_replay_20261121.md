# STEP457 — Offline algorithm replay

Source of truth: Drive `1DwexrLN9XU1vyYml04jocMo9-Y2GtJ2h` (`app/infra_gpu_autoscaling.py`). FastAPI route: `1F5z8PpgaWzoW3aaXWSlrCRVHUeTR0dC4`.

Executed in isolated local Python: **10/10 PASS**, `python -m unittest -v test_real_engine`. Original decision algorithm was manually transcribed from the Drive source into a standalone offline test harness. Adapter source was likewise transcribed from GitHub. These are not byte-identical copies of the canonical source; no HTTP FastAPI integration or canonical deployment is claimed.

SHA-256 local harness: `b884d0c02c1b7849e24f22e043bb6638ff21f536ab3dc0dbd5b79e4846650fb6`; adapter transcript: `65c30115fb1de92f69f568b0ae0b39b8e75dbd90d384df0cb7dda491d22aaaf4`; log: `d3d49db97b6966d0caa1b594e4712158d0289799895a0dabd8f5252f00b007d4`.

Outcome: zero-cost policy blocks scale-out authorization; current capacity unchanged. Remaining: exact canonical module integration and FastAPI HTTP tests. `E2E_CERTIFIED=FALSE | MAIN=INTACTA | PAPER_ONLY=TRUE | COST=R$0`.
