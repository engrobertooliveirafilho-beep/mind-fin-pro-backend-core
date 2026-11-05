# ET-660 — S20 writer and serializer trace: new evidence, fail-closed (2026-11-05)

## New authenticated Drive evidence
- `TRADER_S21_R13_R2D_R6_R3_FINAL_REPORT.txt` ID `1HHxQqEn0kPJxIZP_7BKygR570UTrvmgo`, run `20260808_074222`: 709 Python sources, 103 writer candidates, 27 symbol-capable writers, 894 duplicate module instances, 17 factory instances, 4 distinct factory hashes, one version conflict; S20 symbol absent. Historical version divergence is proven, not the authority of any current copy.
- `TRADER_S21_R13_R2D_R7_R3_R1_FINAL_REPORT.txt` ID `1omqkr9bOU9wHTNNILp834WMvS4UIj3mi`, run `20260810_203510`: 3,750 source files, 73 ranked materializer candidates, **0 strong**, canonical materializer file/hash NULL. 204 record-structure evidence rows and 8 symbol evidence rows. No patch/replay/outcome.
- `TRADER_S21_R13_R2D_R8_R1_FINAL_REPORT.txt` ID `1_OvXD3nfaiX8I_mGyHMhSCJ1Mu968Qd6`, run `20260811_073217`: 709 Python sources, 474 decision function nodes, 2,174 call graph edges, 59 symbol nodes, 26 persistence nodes. `BREAKPOINT_RESOLVED=True` at `mind_trader/reports/P1721_TO_P1735_MARKET_INTELLIGENCE_FUSION/p1721_to_p1735_fusion_stack.py` function `load`; `SYMBOL_PRESENT_AT_PERSISTENCE_NODE_BUT_NOT_IN_S20_OUTPUT_SCHEMA`. No patch/replay/outcome.
- Prior `TRADER_S21_R13_R2D_R9_B_FINAL_REPORT.txt` ID `1I9iYbJTpUMedwcpYmpvGTthFG6O2RSN5`: serializer unresolved, no callee module or canonical serializer hash. A reported breakpoint is not a proven write call.

## Authenticated GitHub code confrontation
Branch `audit/et651-paper-execution-chain-20261105`:
- `app/runtime/mind_trader_institutional_wiring.py`, Git blob SHA `c4cb0cb6759c2df6c7c6717d5708372c0b7c26b4`, is an import/run/health aggregator; not proven equivalent to historical factory SHA-256 `3E4A66308FDF69BEEC2A1DE3309C68A14F8AD285787CD63EAF56A0FB237B7C42`.
- `mind_trader/reports/P1721_TO_P1735_MARKET_INTELLIGENCE_FUSION/p1721_to_p1735_fusion_stack.py`, Git blob SHA `26e4352c02ce15a21882ed762c5c992b1053c5fa`, has `load(p,default=[])` implemented as `json.loads(p.read_text(...))`. This **reads** JSON and is not itself evidence of S20 decision serialization or `day+tick` writes.
- Git blob SHA-1 is not SHA-256. No original historical source bytes were recovered in this ET; no source SHA-256 comparison can be certified.

## Explicit status
Canonical original factory **not recovered by verified SHA-256**; canonical serializer **not identified**; `day+tick -> symbol -> realized outcome` **not proven**. S20 historical 84,000 decisions have 0 verified symbol joins. Do not invent links, patch schema, duplicate engines, promote strategies, or run live orders. No new runtime tests this stage. `S21_CERTIFIED=FALSE`, `FTMO_BLOCKED`, `PAPER_ONLY`, `REAL_ORDERS=0`.
